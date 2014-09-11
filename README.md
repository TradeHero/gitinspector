#### Important note

1. **Running on Linux environment**:
Python `subprocess.Popen` method does not work very well with `dash`, the default shell of some Linux distroes, for instance: Ubuntu. We need `bash` for running `gitinspector`. To change default shell from `dash` to `bash`, use following command:
`ln -sf /bin/bash /bin/sh`


#### For inspecting C# project

use `--file-types=less,htm,cshtml,cs,txt,Config,html,config,css,rb,asax,sql,js,scss,md,aspx`

#### For inspecting iOS project

use `--file-types=markdown,mdown,md,c,storyboard,d,mm,h,m,sh,cpp,strings`

#### For inspecting Android project

use `--file-types=xml,md,java,aidl,properties,gradle`
