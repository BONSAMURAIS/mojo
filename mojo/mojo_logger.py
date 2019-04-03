#mojo_logger.py
import logging
import os
import getpass
import shutil

def Logger(log_dir, project_name, caller_path, copy_script=False,
                                  copy_config=False, config_file=None):
    """The Logger function initialises a logger instance.
    It sets up the log_dir, and if copy_script and/or copy_config
    are set to true and the config file and caller path provided
    it will copy the current version of the caller script and cofig
    file to the log dir too.
    
    RETURNS: logger instance with handlers to file and console with level INFO.
    This instance can be further used by the script calling upon this Logger
    function and be passed on to different functions for your convenience.
    It already logs the username, project name and the script calling upon this
    function.

    log_dir     :   path to directory in which to log the files. Note that this
                    this directory will be new directory called 'log_dir' within
                    the passed directory.

    project_name:   Name of the project, will be logged into thw logging file.

    copy_config :   Boolean indicating whether to copy the config file.
                    Default = False

    config_file :   If copy_config = True, this is the config file being copied.

    copy_script :   Boolean indicating whether to copy the caller script file.
                    Default = False

    caller_path :   The path of the script that called the logger function.
                    if copy_script = True it will also be copied to the log_dir
    """


    #make frsh logging dir
    log_dir = os.path.join(log_dir, 'log')
    os.system('rm -Rf {}'.format(log_dir))
    os.makedirs(log_dir)

    # DEFINE LOG TOOL
    log = logging.getLogger(project_name)
    log.setLevel(logging.INFO)
    log.handlers = []                            # reset handlers
    ch = logging.StreamHandler()                 # set console handler
    ch.setLevel(logging.INFO)                    # set level
    fh = logging.FileHandler(os.path.join(log_dir, #set file handler
                             '{}.log'.format(os.path.splitext(
                             os.path.basename(caller_path))[0])))
    fh.setLevel(logging.INFO)
    aformat = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(aformat)
    fh.setFormatter(formatter)
    log.addHandler(fh)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    # RECORD OBJECT/PROJECT IDENTITY TO LOG
    log.info('USER: {}'.format(getpass.getuser()))
    log.info('PROJECT NAME: ' + project_name)
    log.info('Logging function called by: {} \n with full path {}'.format(
                                    os.path.basename(caller_path),
                                    os.path.realpath(caller_path)))

    if copy_script:
        shutil.copy(caller_path, os.path.join(log_dir,
                                              os.path.basename(caller_path)))
        log.info('copied caller script {} to the the logging dir {}'.format(
                                                        caller_path,log_dir))
    if copy_config:
        shutil.copy(config_file, os.path.join(log_dir,
                                         os.path.basename(config_file)))
        log.info('copied config file {} to the the logging dir {}'.format(
                                                   config_file,log_dir))
    return log


def LogMessage(name, message):
    """add the the (function-) name to the message"""
    new_message = '{} - {}'.format(name, message)
    return new_message
