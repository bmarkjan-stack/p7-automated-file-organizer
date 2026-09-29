; Inno Setup script for the Automated File Organizer.
;
; 1. Build the .exe first: run build_scripts\build_exe.bat (creates dist\FileOrganizer.exe)
; 2. Install Inno Setup: https://jrsoftware.org/isinfo.php
; 3. Open this file in Inno Setup (or right-click -> Compile) to produce
;    an installer at installer\Output\FileOrganizerSetup.exe
;
; Keep MyAppVersion in sync with organizer/version.py and CHANGELOG.md.

#define MyAppName "Automated File Organizer"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "Automated File Organizer"
#define MyAppExeName "FileOrganizer.exe"

[Setup]
AppId={{B6C4D9F1-4C7E-4C8B-9C2A-5D8F3E7A1B90}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=FileOrganizerSetup
Compression=lzma
SolidCompression=yes
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
