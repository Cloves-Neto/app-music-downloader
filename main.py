import sys
import os
import yt_dlp
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFileDialog, QProgressBar,
                             QComboBox, QTextEdit, QListWidget, QListWidgetItem)
# CORREÇÃO 1: Adicionado pyqtSlot à lista de importação
from PyQt6.QtCore import QThread, QObject, pyqtSignal, Qt, pyqtSlot
from PyQt6.QtGui import QColor

# --- Worker para extrair informações da Playlist ---
class PlaylistWorker(QObject):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    def __init__(self, playlist_url):
        super().__init__()
        self.playlist_url = playlist_url
    def run(self):
        try:
            ydl_opts = {'extract_flat': True, 'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(self.playlist_url, download=False)
                if 'entries' in result:
                    self.finished.emit([entry['url'] for entry in result['entries']])
                else: self.error.emit("Nenhum vídeo encontrado na playlist.")
        except Exception as e: self.error.emit(f"Erro ao processar playlist: {str(e)}")

# --- Worker de Download (com a correção no decorador) ---
class DownloaderWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(dict)

    # CORREÇÃO 2: Trocado @pyqtSignal por @pyqtSlot
    @pyqtSlot(str, str, str)
    def start_download(self, url_ou_nome, pasta_destino, formato_escolhido):
        try:
            ydl_opts = {}
            if formato_escolhido == 'MP3 (Áudio)':
                ydl_opts = {'format': 'bestaudio/best', 'outtmpl': os.path.join(pasta_destino, '%(title)s.%(ext)s'), 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}], 'default_search': 'ytsearch', 'noplaylist': True, 'progress_hooks': [self.progress_hook]}
            elif formato_escolhido == 'MP4 (Vídeo)':
                ydl_opts = {'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 'outtmpl': os.path.join(pasta_destino, '%(title)s.mp4'), 'default_search': 'ytsearch', 'noplaylist': True, 'progress_hooks': [self.progress_hook]}

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url_ou_nome])
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    def progress_hook(self, d):
        if d['status'] in ['downloading', 'finished']: self.progress.emit(d)

# --- Interface Gráfica Principal com Thread Persistente ---
class MediaDownloaderApp(QWidget):
    # Sinal para enviar tarefas para o worker
    request_download = pyqtSignal(str, str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Media Downloader Pro (Estável)')
        self.setGeometry(100, 100, 650, 550)

        self.download_queue = []
        self.current_index = -1
        self.is_queue_running = False
        self.is_paused = False
        self.playlist_workers_active = 0

        self.setup_ui()
        self.setup_persistent_worker()
        self.update_button_states()
        self.show()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.input_label = QLabel('Cole nomes, URLs de vídeos ou de playlists (um por linha):')
        self.multi_line_input = QTextEdit()
        self.layout.addWidget(self.input_label)
        self.layout.addWidget(self.multi_line_input)

        config_layout = QHBoxLayout()
        self.format_label = QLabel('Formato:')
        self.format_combo = QComboBox()
        self.format_combo.addItems(['MP3 (Áudio)', 'MP4 (Vídeo)'])
        self.browse_button = QPushButton('Salvar em...')
        self.browse_button.clicked.connect(self.browse_folder)
        self.save_path_label = QLabel(self.get_default_path())
        self.save_path_label.setStyleSheet("font-style: italic;")
        config_layout.addWidget(self.format_label)
        config_layout.addWidget(self.format_combo)
        config_layout.addWidget(self.browse_button)
        config_layout.addWidget(self.save_path_label, 1)
        self.layout.addLayout(config_layout)

        self.start_queue_button = QPushButton('Analisar e Iniciar Downloads')
        self.start_queue_button.clicked.connect(self.build_queue)
        self.layout.addWidget(self.start_queue_button)

        queue_controls_layout = QHBoxLayout()
        self.remove_button = QPushButton('Remover Selecionado')
        self.remove_button.clicked.connect(self.remove_selected_item)
        self.pause_resume_button = QPushButton('Pausar Fila')
        self.pause_resume_button.clicked.connect(self.toggle_pause_resume)
        self.cancel_button = QPushButton('Cancelar Tudo')
        self.cancel_button.clicked.connect(self.cancel_all)
        queue_controls_layout.addWidget(self.remove_button)
        queue_controls_layout.addWidget(self.pause_resume_button)
        queue_controls_layout.addWidget(self.cancel_button)
        self.layout.addLayout(queue_controls_layout)

        self.queue_list_widget = QListWidget()
        self.layout.addWidget(self.queue_list_widget)

        self.progress_bar = QProgressBar()
        self.status_label = QLabel('Pronto para iniciar.')
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.status_label)

    def setup_persistent_worker(self):
        """Cria e inicia a thread e o worker que viverão durante toda a execução."""
        self.worker_thread = QThread()
        self.downloader = DownloaderWorker()
        self.downloader.moveToThread(self.worker_thread)

        # Conecta o sinal da GUI para o slot do worker
        self.request_download.connect(self.downloader.start_download)

        # Conecta os sinais do worker de volta para a GUI
        self.downloader.finished.connect(self.on_download_finished)
        self.downloader.error.connect(self.on_download_error)
        self.downloader.progress.connect(self.update_progress)

        self.worker_thread.start()

    def closeEvent(self, event):
        """Garante que a thread seja finalizada ao fechar a janela."""
        self.worker_thread.quit()
        self.worker_thread.wait()
        super().closeEvent(event)

    # --- Métodos de Controle ---
    def toggle_pause_resume(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.status_label.setText("Fila pausada.")
        else:
            self.status_label.setText("Retomando a fila...")
            self.download_next_item()
        self.update_button_states()

    def cancel_all(self):
        self.status_label.setText("Cancelando downloads...")
        self.download_queue.clear()
        self.is_paused = False
        self.is_queue_running = False
        self.queue_list_widget.clear()
        self.progress_bar.setValue(0)
        self.status_label.setText("Downloads cancelados. A fila está vazia.")
        self.update_button_states()

    def remove_selected_item(self):
        if not self.queue_list_widget.selectedItems() or self.is_queue_running: return
        row = self.queue_list_widget.row(self.queue_list_widget.selectedItems()[0])
        self.download_queue.pop(row)
        self.queue_list_widget.takeItem(row)

    def update_button_states(self):
        is_running = self.is_queue_running
        is_paused = self.is_paused
        self.start_queue_button.setEnabled(not is_running)
        self.remove_button.setEnabled(not is_running and self.queue_list_widget.count() > 0)
        self.pause_resume_button.setEnabled(is_running)
        self.cancel_button.setEnabled(is_running)
        self.pause_resume_button.setText("Retomar Fila" if is_paused else "Pausar Fila")

    # --- Lógica da Fila e Download ---
    def build_queue(self):
        if self.is_queue_running: return
        items = self.multi_line_input.toPlainText().strip().split('\n')
        self.download_queue.clear()
        self.queue_list_widget.clear()
        playlists_to_process = [item for item in (i.strip() for i in items if i.strip()) if self.is_playlist(item)]
        self.download_queue = [item for item in (i.strip() for i in items if i.strip()) if not self.is_playlist(item)]
        self.multi_line_input.clear()
        self.update_button_states()
        if not playlists_to_process and not self.download_queue:
            self.status_label.setText("Nenhum item válido para baixar."); return
        for item in self.download_queue: self.add_item_to_list_widget(item)
        if playlists_to_process:
            self.status_label.setText(f"Processando {len(playlists_to_process)} playlist(s)...")
            self.playlist_workers_active = len(playlists_to_process)
            for url in playlists_to_process: self.process_playlist(url)
        else: self.start_download_queue()

    def download_next_item(self):
        if self.is_paused: return
        if self.current_index >= len(self.download_queue):
            self.status_label.setText("Fila de downloads concluída!")
            self.is_queue_running = False
            self.update_button_states()
            return

        current_list_item = self.queue_list_widget.item(self.current_index)
        current_url = self.download_queue[self.current_index]
        current_list_item.setText(f"Baixando... - {current_url}")
        current_list_item.setForeground(QColor('blue'))
        self.status_label.setText(f"Baixando item {self.current_index + 1}/{len(self.download_queue)}")
        self.progress_bar.setValue(0)
        self.request_download.emit(current_url, self.save_path_label.text(), self.format_combo.currentText())

    def on_download_finished(self):
        if not self.is_queue_running: return
        current_list_item = self.queue_list_widget.item(self.current_index)
        if current_list_item:
            current_list_item.setText(f"✓ Concluído - {self.download_queue[self.current_index]}")
            current_list_item.setForeground(QColor('green'))
        self.current_index += 1
        self.download_next_item()

    def on_download_error(self, error_message):
        if not self.is_queue_running: return
        current_list_item = self.queue_list_widget.item(self.current_index)
        if current_list_item:
            current_list_item.setText(f"✗ Erro - {self.download_queue[self.current_index]}")
            current_list_item.setForeground(QColor('red'))
        print(f"Erro ao baixar: {error_message}")
        self.current_index += 1
        self.download_next_item()

    def start_download_queue(self):
        if not self.download_queue:
            self.status_label.setText("Nenhum vídeo para baixar."); return
        self.is_queue_running = True
        self.current_index = 0
        self.update_button_states()
        self.download_next_item()

    # --- Métodos Utilitários ---
    def get_default_path(self):
        path = os.path.join(os.path.expanduser('~'), 'Downloads')
        os.makedirs(path, exist_ok=True)
        return path
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Selecione a Pasta', self.get_default_path())
        if folder: self.save_path_label.setText(folder)
    def is_playlist(self, text):
        return "youtube.com/playlist?list=" in text or "youtu.be/" in text and "list=" in text
    def process_playlist(self, url):
        thread = QThread()
        worker = PlaylistWorker(url)
        worker.moveToThread(thread)
        thread.finished.connect(thread.deleteLater)
        worker.finished.connect(worker.deleteLater)
        worker.error.connect(worker.deleteLater)
        worker.finished.connect(self.on_playlist_processed)
        worker.error.connect(self.on_playlist_error)
        thread.started.connect(worker.run)
        thread.start()
        setattr(self, f"temp_thread_{url}", thread)
    def on_playlist_processed(self, video_urls):
        self.download_queue.extend(video_urls)
        for url in video_urls: self.add_item_to_list_widget(url)
        self.playlist_workers_active -= 1
        if self.playlist_workers_active == 0: self.start_download_queue()
    def on_playlist_error(self, error_message):
        print(error_message)
        self.playlist_workers_active -= 1
        if self.playlist_workers_active == 0: self.start_download_queue()
    def add_item_to_list_widget(self, text):
        list_item = QListWidgetItem(f"Aguardando - {text}")
        list_item.setForeground(QColor('gray'))
        self.queue_list_widget.addItem(list_item)
    def update_progress(self, data):
        if data['status'] == 'downloading':
            total = data.get('total_bytes') or data.get('total_bytes_estimate')
            if total:
                percent = int((data.get('downloaded_bytes', 0) / total) * 100)
                self.progress_bar.setValue(percent)

# --- Execução da Aplicação ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MediaDownloaderApp()
    sys.exit(app.exec())