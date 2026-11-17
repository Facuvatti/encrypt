#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

if [ -z "${PREFIX:-}" ] || [ ! -d "$PREFIX/bin" ]; then
  echo "Este instalador está pensado para Termux en Android." >&2
  exit 1
fi

echo "Instalando dependencias de Encrypt..."
pkg update -y
pkg install -y python python-numpy curl tar

INSTALL_DIR="$HOME/.local/share/encrypt"
mkdir -p "$INSTALL_DIR" "$PREFIX/bin"

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

echo "Descargando el código fuente..."
curl -fL "https://codeload.github.com/Facuvatti/encrypt/tar.gz/refs/heads/main" -o "$tmp_dir/source.tar.gz"
tar -xzf "$tmp_dir/source.tar.gz" --strip-components=1 -C "$INSTALL_DIR"

cat > "$PREFIX/bin/encrypt" <<'LAUNCHER'
#!/data/data/com.termux/files/usr/bin/bash
exec python "$HOME/.local/share/encrypt/encrypt.py" "$@"
LAUNCHER

cat > "$PREFIX/bin/decrypt" <<'LAUNCHER'
#!/data/data/com.termux/files/usr/bin/bash
exec python "$HOME/.local/share/encrypt/decrypt.py" "$@"
LAUNCHER

chmod 755 "$PREFIX/bin/encrypt" "$PREFIX/bin/decrypt"

python -c 'import numpy' || {
  echo "No se pudo importar NumPy. Revisá la instalación de python-numpy." >&2
  exit 1
}

echo
echo "Encrypt quedó instalado en Termux."
echo "Probá: encrypt --help"
echo "      decrypt --help"
