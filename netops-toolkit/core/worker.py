from PySide6.QtCore import QThread, Signal
class Worker(QThread):
    done=Signal(object)
    failed=Signal(str)
    def __init__(self,fn,*args):
        super().__init__(); self.fn=fn; self.args=args
    def run(self):
        try: self.done.emit(self.fn(*self.args))
        except Exception as exc: self.failed.emit(str(exc))
