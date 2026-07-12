"""
Pre-processing task: decrypt a PGP-encrypted file.

Requires the optional dependency `python-gnupg` (wraps the system `gpg`
binary):   pip install python-gnupg

Key material is never hard-coded in config.json. `secret_reference` is a
lookup key resolved via `resolve_secret()`, which you should point at your
actual secret store (Vault, AWS Secrets Manager, Azure Key Vault, env vars,
etc). A minimal env-var-based resolver is provided so this runs out of the
box in dev/test environments.
"""

from __future__ import annotations
import os

from etl_framework.core.base import PreProcessingTask
from etl_framework.core.context import PipelineContext


def resolve_secret(secret_reference: str) -> str:
    """
    Resolve a secret_reference (e.g. 'pgp/private/key') to an actual secret value.

    Default implementation: look up an environment variable derived from the
    reference (slashes -> underscores, upper-cased). Swap this out for a real
    secrets-manager client in production, e.g.:

        import boto3
        def resolve_secret(secret_reference):
            client = boto3.client("secretsmanager")
            return client.get_secret_value(SecretId=secret_reference)["SecretString"]
    """
    env_var = secret_reference.upper().replace("/", "_").replace("-", "_")
    value = os.environ.get(env_var)
    if value is None:
        raise KeyError(
            f"Could not resolve secret_reference='{secret_reference}' "
            f"(expected env var '{env_var}' to be set)"
        )
    return value


class PGPDecryptor(PreProcessingTask):
    """
    parameters:
        input_path       : path to the .pgp/.gpg encrypted file
        secret_reference  : lookup key for the private key / passphrase
        output_path       : (optional) decrypted output path; defaults to
                             input_path with the trailing .pgp/.gpg stripped
    """

    def execute(self, context: PipelineContext) -> PipelineContext:
        input_path = self.parameters["input_path"]
        secret_reference = self.parameters["secret_reference"]
        output_path = self.parameters.get("output_path") or self._default_output_path(input_path)

        if not os.path.exists(input_path):
            self.logger.warning("Encrypted input not found: %s (skipping decrypt)", input_path)
            return context

        try:
            import gnupg  # python-gnupg
        except ImportError:
            self.logger.warning(
                "python-gnupg not installed; skipping actual decryption. "
                "Install with `pip install python-gnupg` and ensure `gpg` is on PATH."
            )
            context.add_file_path(input_path)
            return context

        private_key = resolve_secret(secret_reference)

        gpg_home = self.parameters.get("gpg_home", os.path.expanduser("~/.gnupg"))
        os.makedirs(gpg_home, exist_ok=True)
        gpg = gnupg.GPG(gnupghome=gpg_home)
        import_result = gpg.import_keys(private_key)
        self.logger.info("Imported %d key(s)", len(import_result.fingerprints))

        passphrase = self.parameters.get("passphrase")  # optional, also resolvable via vault
        with open(input_path, "rb") as f:
            status = gpg.decrypt_file(f, output=output_path, passphrase=passphrase)

        if not status.ok:
            raise RuntimeError(f"PGP decryption failed: {status.status}")

        context.add_file_path(output_path)
        context.set_meta("last_decrypted_file", output_path)
        self.logger.info("Decrypted %s -> %s", input_path, output_path)
        return context

    @staticmethod
    def _default_output_path(input_path: str) -> str:
        for suffix in (".pgp", ".gpg"):
            if input_path.endswith(suffix):
                return input_path[: -len(suffix)]
        return input_path + ".decrypted"
