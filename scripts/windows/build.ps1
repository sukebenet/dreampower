Set-Location ../..

#
# CLI.
# The CLI is where the neural network is located.
#
# Requirements:
# * Python 3.6 and pip3
# * CUDA 10.0
#

# PyInstaller will begin to compile the script and package
# everything necessary in a directory with the final .exe
# Relax and enjoy your coffee :)

pyinstaller main.py -y --onedir --name "cli" --add-binary "./third/msvcp/msvcp140.dll;."


#
# Success
#

Write-Output ("Build completed!")
Write-Output ("It should have generated a folder called dist/, inside you will find the final project files that you can share with everyone!")
Write-Output ("Enjoy and remember to respect the License!")