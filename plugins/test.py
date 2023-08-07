import tools
import re




regex = "root:[x*]:0:0:"
result = re.findall(regex, 'root:x:0:0:root:/root:/bin/bash')

print(result)
