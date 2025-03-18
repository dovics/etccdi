@echo off

for %%v in (ssp126 ssp245 ssp370 ssp585) do (
    echo Processing: %%v
    
    powershell -Command "(gc config.py) -replace 'mode = \".*\"', 'mode = \"%%v\"' | Out-File -encoding UTF8 config.py"
    
    echo Starting main.py...
    python main.py
    
    echo Finished processing %%v
    echo ------------------------
)