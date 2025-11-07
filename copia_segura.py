import shutil
import os
import hashlib
import time
from tkinter import filedialog, Tk

# =======================================================
# 1. CONFIGURAÇÕES - SELEÇÃO DE PASTA
# =======================================================

print("Abrindo janelas para seleção de pastas...")

# Cria uma "janela" raiz invisível
root = Tk()
root.withdraw()

# Abre o seletor para a ORIGEM
print("Por favor, selecione a PASTA DE ORIGEM (de onde copiar)...")
PASTA_ORIGEM = filedialog.askdirectory(title="Selecione a PASTA DE ORIGEM")

# Abre o seletor para o DESTINO
print("Por favor, selecione a PASTA DE DESTINO (pendrive)...")
PASTA_DESTINO = filedialog.askdirectory(title="Selecione a PASTA DE DESTINO")

# Verifica se o usuário cancelou
if not PASTA_ORIGEM or not PASTA_DESTINO:
    print("Seleção cancelada. O script não será executado.")
    exit() # Encerra o script

# Configurações de cópia
TEMPO_ESPERA = 1.0  # Tempo (em segundos) para o OS finalizar a escrita
TENTATIVAS_MAXIMAS = 4 # Tentativas de verificação antes de desistir
# =======================================================

# =======================================================
# 2. FUNÇÃO DE HASH (Verificação)
# =======================================================
def hash_md5(caminho_arquivo):
    """Calcula o hash MD5 de um arquivo."""
    hash_obj = hashlib.md5()
    try:
        with open(caminho_arquivo, "rb") as f:
            # Lê o arquivo em pedaços para não lotar a memória
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        print(f"  [ERRO HASH] Não foi possível ler {caminho_arquivo}: {e}")
        return None
# =======================================================


# =======================================================
# 3. LOOP PRINCIPAL DE CÓPIA
# =======================================================
print("-" * 50)
print(f"Iniciando cópia segura de:")
print(f"Origem:  {PASTA_ORIGEM}")
print(f"Destino: {PASTA_DESTINO}")
print("-" * 50)

arquivos_totais = 0
arquivos_copiados = 0
arquivos_falhados = 0

# os.walk() "anda" por todas as pastas e subpastas
for dirpath, dirnames, filenames in os.walk(PASTA_ORIGEM):

    # 1. Calcula o caminho relativo (ex: "Musicas/Rock")
    # Isso é crucial para replicar a estrutura de pastas no destino
    caminho_relativo = os.path.relpath(dirpath, PASTA_ORIGEM)

    # 2. Calcula o caminho de destino completo
    # Se caminho_relativo for ".", não o adicione
    if caminho_relativo == ".":
        pasta_destino_atual = PASTA_DESTINO
    else:
        pasta_destino_atual = os.path.join(PASTA_DESTINO, caminho_relativo)

    # 3. Cria as subpastas no destino, se não existirem
    if not os.path.exists(pasta_destino_atual):
        print(f"\n[Criando pasta]: {pasta_destino_atual}")
        os.makedirs(pasta_destino_atual)

    # 4. Itera sobre os arquivos da pasta atual
    for file in filenames:
        arquivos_totais += 1
        caminho_origem = os.path.join(dirpath, file)
        caminho_destino = os.path.join(pasta_destino_atual, file)

        print(f"\nProcessando: {file}")

        try:
            # --- CÁLCULO DO HASH DE ORIGEM ---
            print("  Calculando hash de origem...")
            hash_origem = hash_md5(caminho_origem)
            if not hash_origem:
                arquivos_falhados += 1
                continue # Pula para o próximo arquivo se não conseguiu ler

            # --- VERIFICA SE JÁ EXISTE NO DESTINO (E BATE O HASH) ---
            if os.path.exists(caminho_destino):
                print("  Arquivo já existe no destino. Verificando...")
                hash_destino_existente = hash_md5(caminho_destino)

                if hash_origem == hash_destino_existente:
                    print("  [OK] Hashes idênticos. Pulando cópia.")
                    arquivos_copiados += 1 # Conta como "copiado" (pois está correto)
                    continue # Pula para o próximo arquivo
                else:
                    print("  [AVISO] Hashes diferentes. O arquivo será sobrescrito.")

            # --- CÓPIA ---
            print(f"  Copiando para {pasta_destino_atual}...")
            shutil.copy2(caminho_origem, caminho_destino) # copy2 preserva metadados

            # --- VERIFICAÇÃO PÓS-CÓPIA ---
            print("  Verificando integridade...")

            tentativa = 0
            hash_destino = None

            # Tenta verificar o hash algumas vezes
            while tentativa < TENTATIVAS_MAXIMAS:
                # Espera para o sistema operacional "soltar" o arquivo
                time.sleep(TEMPO_ESPERA)

                hash_destino = hash_md5(caminho_destino)
                if hash_destino: # Se conseguiu ler o hash
                    break

                tentativa += 1
                print(f"  Falha ao ler hash do destino. Tentando novamente ({tentativa}/{TENTATIVAS_MAXIMAS})...")

            # --- COMPARAÇÃO FINAL ---
            if hash_origem == hash_destino:
                print("  [SUCESSO] Verificado! Os hashes são idênticos.")
                arquivos_copiados += 1
            else:
                print(f"  [ERRO FATAL] Os hashes NÃO BATEM após a cópia!")
                print(f"  Origem:  {hash_origem}")
                print(f"  Destino: {hash_destino}")
                arquivos_falhados += 1

        except Exception as e:
            print(f"  [ERRO INESPERADO] ao processar {file}: {e}")
            arquivos_falhados += 1

# =======================================================
# 4. RELATÓRIO FINAL
# =======================================================
print("\n" + "=" * 50)
print("CÓPIA CONCLUÍDA")
print(f"Arquivos totais na origem: {arquivos_totais}")
print(f"Arquivos verificados/copiados: {arquivos_copiados}")
print(f"Arquivos com falha: {arquivos_falhados}")
print("=" * 50)

# Pausa final para o usuário ler o resultado
input("Pressione Enter para fechar...")