^!Enter::
; Change directory to where your script is located
SetWorkingDir, C:\Users\james\Documents\GitHub\dodec

; For virtual environment
Run, cmd /c "claude-env\Scripts\activate && python main.py", , Hide

return