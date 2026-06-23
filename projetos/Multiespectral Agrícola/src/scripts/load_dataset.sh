#!/usr/bin/env sh

set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
DATASET_DIR="$PROJECT_ROOT/data/dataset"
S3_SOURCE="s3://intelinair-data-releases/agriculture-vision/cvpr_challenge_2021/supervised"
DOTENV_FILE="$PROJECT_ROOT/.env"

echo "Verificando pasta do dataset em: $DATASET_DIR"

should_download=1
if [ -d "$DATASET_DIR" ] && [ "$(ls -A "$DATASET_DIR" 2>/dev/null)" ]; then
	echo "Pasta data/dataset já existe e contém arquivos. Download será pulado."
	should_download=0
fi

mkdir -p "$DATASET_DIR"

if [ "$should_download" -eq 1 ]; then
	if ! command -v aws >/dev/null 2>&1; then
		echo "Erro: comando 'aws' não encontrado no sistema."
		echo "Instale o AWS CLI e tente novamente."
		echo "Linux (pip):   pip install awscli"
		echo "Ubuntu/Debian: sudo apt-get install -y awscli"
		echo "Documentação:  https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
		exit 1
	fi

	echo "Iniciando download do dataset..."
	if aws s3 cp "$S3_SOURCE" "$DATASET_DIR" --no-sign-request --recursive; then
		echo "Download concluído com sucesso em: $DATASET_DIR"
	else
		echo "Falha ao executar o comando aws s3 cp."
		echo "Verifique se o AWS CLI está instalado e acessível no PATH."
		echo "Documentação de instalação: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
		exit 1
	fi
fi

SUPERVISED_DIR="$DATASET_DIR/supervised"
DATASET_PATH_VALUE="$SUPERVISED_DIR/Agriculture-Vision-2021"

write_dotenv_if_dataset_exists() {
	if [ -d "$DATASET_PATH_VALUE" ]; then
		printf 'DATASET_PATH=%s\n' "$DATASET_PATH_VALUE" > "$DOTENV_FILE"
		echo "Arquivo .env gerado em: $DOTENV_FILE"
		echo "DATASET_PATH configurado para: $DATASET_PATH_VALUE"
		return 0
	fi

	return 1
}

if [ ! -d "$SUPERVISED_DIR" ]; then
	echo "Pasta 'supervised' não encontrada em: $SUPERVISED_DIR"
	echo "Nada para descompactar."
	if write_dotenv_if_dataset_exists; then
		echo "Processo finalizado."
	fi
	exit 0
fi

tar_list_file=$(mktemp)
trap 'rm -f "$tar_list_file"' EXIT INT TERM
find "$SUPERVISED_DIR" -maxdepth 1 -type f -name "*.tar.gz" > "$tar_list_file"

if [ ! -s "$tar_list_file" ]; then
	echo "Nenhum arquivo .tar.gz encontrado em: $SUPERVISED_DIR"
	if write_dotenv_if_dataset_exists; then
		echo "Dataset já parece estar descompactado."
		echo "Processo finalizado."
	else
		echo "Aviso: diretório esperado não encontrado: $DATASET_PATH_VALUE"
		echo "Arquivo .env não foi gerado."
	fi
	exit 0
fi

total_bytes=0
while IFS= read -r tar_file; do
	file_bytes=$(wc -c < "$tar_file" | tr -d ' ')
	total_bytes=$((total_bytes + file_bytes))
done < "$tar_list_file"

if command -v numfmt >/dev/null 2>&1; then
	required_space_human=$(numfmt --to=iec --suffix=B "$total_bytes")
else
	required_space_human="${total_bytes} bytes"
fi

echo "Arquivos .tar.gz encontrados para descompactar:"
cat "$tar_list_file"
echo
echo "Espaço adicional estimado necessário para descompactar: $required_space_human"
echo "Aviso: mantenha pelo menos esse espaço livre em disco antes de continuar."
printf 'Deseja continuar com a descompactação? [s/N]: '
read -r user_answer

case "$user_answer" in
	s|S|sim|SIM|y|Y|yes|YES)
		;;
	*)
		echo "Descompactação cancelada pelo usuário."
		if write_dotenv_if_dataset_exists; then
			echo "Processo finalizado."
		fi
		exit 0
		;;
esac

while IFS= read -r tar_file; do
	tar_size_human=$(du -h "$tar_file" | awk '{print $1}')
	echo "Descompactando $tar_file (tamanho: $tar_size_human)..."
	if tar -xzf "$tar_file" -C "$SUPERVISED_DIR"; then
		echo "Descompactação concluída para: $tar_file"
		rm -f "$tar_file"
		echo "Arquivo removido após sucesso: $tar_file"
	else
		echo "Falha ao descompactar: $tar_file"
		echo "Arquivo .tar.gz foi mantido para nova tentativa."
		exit 1
	fi
done < "$tar_list_file"

if write_dotenv_if_dataset_exists; then
:
else
	echo "Aviso: diretório esperado não encontrado após descompactação: $DATASET_PATH_VALUE"
	echo "Arquivo .env não foi gerado."
	exit 1
fi

echo "Processo finalizado."