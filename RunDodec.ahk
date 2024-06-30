^!Enter::
; Change directory to where your script is located
SetWorkingDir, [Path to repo folder]

; For virtual environment
Run, cmd /c "claude-env\Scripts\activate && python main.py", , Hide

return