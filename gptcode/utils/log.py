import logging

import gptcode

FORMAT = '%(asctime)s - %(thread)d - %(filename)s-%(module)s:%(lineno)s - %(levelname)s: %(message)s'
logging.basicConfig(format=FORMAT)

gptcode_log = logging.getLogger(f'gptcode:{gptcode.__version__}')