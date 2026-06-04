; Inno Setup 安装包脚本 — DiligenceBinder
; 用法: 用 Inno Setup Compiler 编译此文件

[Setup]
AppName=DiligenceBinder
AppVersion=1.0
AppPublisher=DiligenceBinder Contributors
DefaultDirName={pf}\DiligenceBinder
DefaultGroupName=DiligenceBinder
OutputDir=.\installer_output
OutputBaseFilename=DiligenceBinder_Setup_v1.0
SetupIconFile=
Compression=lzma2/ultra64
SolidCompression=yes
UninstallDisplayName=DiligenceBinder
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "chinese"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Files]
; PyInstaller 生成的 exe
Source: "dist\DiligenceBinder.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; 桌面快捷方式
Name: "{commondesktop}\DiligenceBinder"; Filename: "{app}\DiligenceBinder.exe"; WorkingDir: "{app}"
; 开始菜单
Name: "{group}\DiligenceBinder"; Filename: "{app}\DiligenceBinder.exe"; WorkingDir: "{app}"
Name: "{group}\卸载 DiligenceBinder"; Filename: "{uninstallexe}"

[Run]
; 安装完成后运行程序
Filename: "{app}\DiligenceBinder.exe"; Description: "启动 DiligenceBinder"; Flags: nowait postinstall skipifsilent
