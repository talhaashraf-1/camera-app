import logging

def setup_logger():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='camera_app.log',
        filemode='w'
    )
    return logging.getLogger('CameraApp')