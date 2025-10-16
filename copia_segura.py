import shutil
import os
import hashlib
import time

# =======================================================
# 1. CONFIGURAÇÕES - AJUSTE ESTES CAMINHOS
# =======================================================
# Substitua pelo caminho da pasta de origem (no seu PC)
PASTA_ORIGEM = 'C:/Users/cloves.neto/Music/Musicas Baixadas'
# Substitua pela letra ou caminho do seu pendrive
PASTA_DESTINO = 'D:'
# Ajuda pendrives lentos.
TEMPO_ESPERA = 1.0
# Limite de quantas vezes tentar copiar um arquivo
TENTATIVAS_MAXIMAS = 4
# =======================================================

def calcular_hash_sha256(caminho_arquivo):
    """Calcula o hash SHA256 do arquivo em blocos."""
    hash_funcao = hashlib.sha256()
    try:
        with open(caminho_arquivo, 'rb') as f:
            # Lê o arquivo em blocos de 4KB para otimizar arquivos grandes
            for bloco in iter(lambda: f.read(4096), b''):
                hash_funcao.update(bloco)
        return hash_funcao.hexdigest()
    except Exception as e:
        # Se houver erro de I/O (entrada/saída), o hash não pode ser calculado.
        return None

# Loop principal de cópia
print("-" * 50)
print(f"Iniciando cópia de {PASTA_ORIGEM} para {PASTA_DESTINO}")
print(f"Máximo de {TENTATIVAS_MAXIMAS} tentativas por arquivo.")
print("-" * 50)

arquivos_copiados = 0
arquivos_falharam_definitivamente = 0

for nome_arquivo in os.listdir(PASTA_ORIGEM):
    caminho_origem = os.path.join(PASTA_ORIGEM, nome_arquivo)
    caminho_destino = os.path.join(PASTA_DESTINO, nome_arquivo)

    # Pula diretórios e links simbólicos, foca apenas em arquivos
    if not os.path.isfile(caminho_origem):
        continue

    print(f"\n[Arquivo] Tentando copiar: {nome_arquivo}")

    # Inicia o ciclo de retentativas
    sucesso = False
    for tentativa in range(1, TENTATIVAS_MAXIMAS + 1):
        if sucesso:
            break

        print(f"    [TENTATIVA {tentativa}/{TENTATIVAS_MAXIMAS}] Iniciando cópia...")

        # Garante que o arquivo corrompido anterior seja removido antes de tentar novamente
        if os.path.exists(caminho_destino):
            try:
                os.remove(caminho_destino)
            except Exception:
                # Pode falhar se o arquivo estiver em uso, mas tentamos
                pass

        # 1. Tenta copiar o arquivo
        try:
            shutil.copy2(caminho_origem, caminho_destino)
            print("    Cópia física concluída. Verificando integridade...")

            # 2. Calcula os hashes
            hash_origem = calcular_hash_sha256(caminho_origem)
            hash_destino = calcular_hash_sha256(caminho_destino)

            # 3. Verifica a integridade
            if hash_origem and hash_destino and hash_origem == hash_destino:
                print(f"    ✅ SUCESSO na Tentativa {tentativa}! Hash verificado (integridade OK).")
                arquivos_copiados += 1
                sucesso = True
            else:
                print(f"    ❌ FALHA na Tentativa {tentativa}: Arquivos são diferentes (corrompido).")
                if tentativa < TENTATIVAS_MAXIMAS:
                    print(f"    Re-tentando em {TEMPO_ESPERA} segundos...")
                else:
                    print("    Máximo de tentativas alcançado.")

        except Exception as e:
            print(f"    [ERRO CRÍTICO] Falha na cópia: {e}")
            if tentativa < TENTATIVAS_MAXIMAS:
                print(f"    Re-tentando em {TEMPO_ESPERA} segundos...")
            else:
                print("    Máximo de tentativas alcançado.")

        # Pausa antes da próxima tentativa (ou da próxima cópia)
        if not sucesso:
             time.sleep(TEMPO_ESPERA)

    if not sucesso:
        print(f"ATENÇÃO: Arquivo {nome_arquivo} FALHOU após {TENTATIVAS_MAXIMAS} tentativas.")
        arquivos_falharam_definitivamente += 1

        # --- NOVIDADE: LIMPEZA FINAL ---
        if os.path.exists(caminho_destino):
            try:
                os.remove(caminho_destino)
                print(f"    🗑️ Arquivo corrompido ({nome_arquivo}) REMOVIDO do pendrive.")
            except Exception as e:
                print(f"    [ERRO DE LIMPEZA] Não foi possível remover o arquivo corrompido: {e}")
        # -------------------------------


print("-" * 50)
print("Processo de cópia e verificação concluído.")
print(f"Total de arquivos copiados e verificados com sucesso: {arquivos_copiados}")
print(f"Total de arquivos que FALHARAM definitivamente e foram limpos: {arquivos_falharam_definitivamente}")
print("-" * 50)