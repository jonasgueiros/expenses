#define MyAppName "expen"
#define MyAppVersion "0.8"
#define MyAppPublisher "Jona G"
#define MyAppURL "https://github.com/jonasgueiros"
#define MyAppExeName "expensys.exe"

[Setup]
AppId={{B7F3B423-9625-40A9-8EB0-C39854135D60}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
PrivilegesRequired=lowest
OutputDir=C:\Users\MACHI\Documents\GitHub\expenses
OutputBaseFilename=expensys
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\MACHI\Documents\GitHub\expenses\dist\expensys\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\MACHI\Documents\GitHub\expenses\dist\expensys\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\MACHI\Documents\GitHub\expenses\requirements.txt"; DestDir: "{tmp}"; Flags: deleteafterinstall
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:ProgramOnTheWeb,{#MyAppName}}"; Filename: "{#MyAppURL}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
Filename: "{cmd}"; Parameters: "/c pip install -r ""{tmp}\requirements.txt"""; Flags: runhidden
