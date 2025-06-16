from pathlib import Path
from langfuse import Langfuse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

lf = Langfuse()

class Push(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith((".j2", ".baml")):
            return
        file = Path(event.src_path)
        lf.upsert_prompt(
            name=file.stem,
            text=file.read_text(),
            label="sandbox"
        )
        print("▲  pushed", file)

observer = Observer()
observer.schedule(Push(), "prompts/", recursive=True)
observer.start()
observer.join()
