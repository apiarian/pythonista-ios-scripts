# copies a file from somewhere in iOS to the current directory

import dialogs
import shutil

fn = dialogs.pick_document(types=['public.item'])

shutil.copy(fn, './')
