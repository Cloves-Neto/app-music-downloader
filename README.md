# App Music Downloader

Este é um aplicativo de desktop para baixar músicas e vídeos do YouTube. Ele foi construído com Python e a interface gráfica utiliza a biblioteca PyQt6\. A funcionalidade de download é fornecida pela poderosa biblioteca `yt-dlp`.

## Funcionalidades

- **Download de Mídia:** Baixe vídeos ou extraia o áudio em formato MP3.
- **Múltiplos Itens:** Adicione vários links de vídeos, nomes de músicas ou links de playlists para baixar em lote.
- **Fila de Downloads:** Os itens adicionados são colocados em uma fila e baixados sequencialmente.
- **Controle da Fila:**

  - **Pausar/Retomar:** Pause a fila de downloads a qualquer momento e retome de onde parou.
  - **Cancelar:** Cancele todos os downloads pendentes e limpe a fila.
  - **Remover:** Remova itens específicos da fila antes de iniciar os downloads.

- **Interface Simples:** Uma interface gráfica intuitiva para facilitar o uso.
- **Seleção de Formato:** Escolha entre baixar o vídeo completo (MP4) ou apenas o áudio (MP3).
- **Seleção de Pasta:** Escolha facilmente onde salvar os arquivos baixados.

## Como Instalar e Rodar o Projeto

### Pré-requisitos

- Python 3.x
- `pip` (gerenciador de pacotes do Python)
- `ffmpeg`: O `yt-dlp` requer o `ffmpeg` para processar os arquivos de áudio e vídeo. Você pode baixá-lo em [ffmpeg.org](https://ffmpeg.org/download.html) e garantir que o executável esteja no PATH do seu sistema.

### Passos para Instalação

1. **Clone o repositório:**

  ```bash
  git clone https://github.com/Cloves-Neto/app-music-downloader.git

  cd app-music-downloader
  ```

2. **Crie e ative um ambiente virtual (recomendado):**

  ```bash
  python -m venv venv
  ```

### No Windows

- venv\Scripts\activate

### No macOS/Linux

- source venv/bin/activate

1. **Instale as dependências:**

  ```bash
  pip install -r requirements.txt
  ```

### Como Rodar a Aplicação

Após instalar as dependências, execute o seguinte comando no seu terminal:

```bash
python main.py
```

Isso abrirá a janela do aplicativo "Media Downloader".

## Como Usar a Aplicação

1. **Adicionar Músicas/Vídeos:**

  - Na caixa de texto grande, cole os links de vídeos do YouTube, links de playlists ou simplesmente digite os nomes das músicas que você deseja procurar e baixar.
  - Você pode adicionar um item por linha para criar uma lista.

2. **Configurar o Download:**

  - **Formato:** No menu suspenso, escolha se deseja baixar como `MP3 (Áudio)` ou `MP4 (Vídeo)`.
  - **Salvar em...:** Clique neste botão para escolher a pasta no seu computador onde os arquivos serão salvos. Por padrão, será a sua pasta de "Downloads".

3. **Iniciar a Fila:**

  - Clique no botão **"Analisar e Iniciar Downloads"**. O aplicativo irá processar os itens (expandindo playlists, se houver) e adicioná-los à fila de downloads abaixo.
  - O processo de download começará automaticamente.

4. **Gerenciar a Fila:**

  - **Pausar Fila:** Clique para pausar o download do item atual e dos próximos. O botão mudará para "Retomar Fila".
  - **Retomar Fila:** Clique para continuar os downloads de onde parou.
  - **Cancelar Tudo:** Interrompe todos os downloads e limpa a fila completamente.
  - **Remover Selecionado:** Antes de iniciar a fila, você pode clicar em um item na lista e depois neste botão para removê-lo.

## Utilitário Adicional: `copia_segura.py`

Este projeto também inclui um script chamado `copia_segura.py`. Ele serve para copiar arquivos de uma pasta de origem para uma de destino (como um pendrive), verificando a integridade dos arquivos para garantir uma cópia sem erros.

Para usá-lo, execute-o diretamente:

```bash
python copia_segura.py
```

Ele abrirá janelas para que você selecione a pasta de origem e a de destino.
