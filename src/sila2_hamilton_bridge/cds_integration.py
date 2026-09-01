class CDSIntegration:
    def __init__(self):
        self.connected = True

    def execute_run(self, parameters):
        if not self.connected:
            raise ConnectionError("CDS system not connected")
        import time
        time.sleep(0.01)
        return True