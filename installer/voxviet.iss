; VoxViet Studio — trình cài đặt (Inno Setup 6). Build:
;   iscc /DAppVersion=0.7.0 installer\voxviet.iss      (cần installer\bin\uv.exe — xem .github/workflows/build.yml)
; Trình cài chép mã nguồn + uv.exe, rồi chạy installer\setup.ps1 để cài Python, thư viện, nối GitHub,
; chuyển dữ liệu bản cũ. Mô hình lõi giọng tải ở lần mở đầu (màn hình chào).

#define AppName "VoxViet Studio"
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif
#define OldDefault "E:\VoiceTriny\voxviet-studio"

[Setup]
AppId={{6BB632F6-503D-4DD4-B6B7-24C889B5AD9E}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher=VoxViet Studio (dùng cá nhân)
DefaultDirName={code:DefaultDir}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
UsePreviousAppDir=yes
DirExistsWarning=no
; Cài cho riêng người dùng này: không cần quyền quản trị, đăng nhập GitHub lưu đúng tài khoản Windows
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=Output
OutputBaseFilename=VoxVietStudio-Setup-{#AppVersion}
SetupIconFile=..\web\voxviet.ico
UninstallDisplayIcon={app}\web\voxviet.ico
UninstallDisplayName={#AppName}
WizardStyle=modern
Compression=lzma2/max
SolidCompression=yes
; Phần mềm đang mở (appmode tạo mutex này) → nhắc đóng trước khi cài đè / gỡ
AppMutex=VoxVietStudio.Running
CloseApplications=no
SetupLogging=yes

[Languages]
#ifexist "Vietnamese.isl"
Name: "vi"; MessagesFile: "Vietnamese.isl"
#else
Name: "en"; MessagesFile: "compiler:Default.isl"
#endif

[Tasks]
Name: "desktopicon"; Description: "Tạo biểu tượng VoxViet Studio trên Desktop"

[Files]
; Mã nguồn (không gồm môi trường, mô hình, dữ liệu, file phát triển)
Source: "..\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; \
  Excludes: "\.git,\.github,\ci-logs,\.venv,\envs,\models,\runtime,\data,\installer,\tests,\.claude,\.thiet-ke,\.pytest_cache,\tools\voxviet-trainer,__pycache__,*.pyc,*.zip"
; Dữ liệu mẫu đi kèm (bộ giọng có sẵn, kịch bản thu, từ điển) — không đè dữ liệu của bạn khi cài lại
Source: "..\data\*"; DestDir: "{app}\data"; Flags: onlyifdoesntexist uninsneveruninstall recursesubdirs createallsubdirs; \
  Excludes: "\outputs,\.local,\.app-window,\settings.json,*.parquet"
Source: "setup.ps1"; DestDir: "{app}\installer"; Flags: ignoreversion
Source: "bin\uv.exe"; DestDir: "{app}\runtime"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\.venv\Scripts\pythonw.exe"; Parameters: """{app}\app.py"" --app"; \
  WorkingDir: "{app}"; IconFilename: "{app}\web\voxviet.ico"; Comment: "Chuyển văn bản thành giọng nói Việt – Anh"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\.venv\Scripts\pythonw.exe"; Parameters: """{app}\app.py"" --app"; \
  WorkingDir: "{app}"; IconFilename: "{app}\web\voxviet.ico"; Tasks: desktopicon
Name: "{autoprograms}\{#AppName} - sửa bản cài"; Filename: "powershell.exe"; \
  Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\installer\setup.ps1"""; WorkingDir: "{app}"

[Run]
Filename: "{app}\.venv\Scripts\pythonw.exe"; Parameters: """{app}\app.py"" --app"; WorkingDir: "{app}"; \
  Description: "Mở VoxViet Studio"; Flags: postinstall nowait skipifsilent unchecked; Check: SetupOk

[UninstallDelete]
; Môi trường & mã (kể cả file do bản cập nhật thêm vào). Kho giọng và mô hình: hỏi khi gỡ.
Type: filesandordirs; Name: "{app}\.venv"
Type: filesandordirs; Name: "{app}\runtime"
Type: filesandordirs; Name: "{app}\envs"
Type: filesandordirs; Name: "{app}\tools"
Type: filesandordirs; Name: "{app}\voxviet"
Type: filesandordirs; Name: "{app}\web"
Type: filesandordirs; Name: "{app}\installer"
Type: filesandordirs; Name: "{app}\tests"
Type: filesandordirs; Name: "{app}\.git"
Type: filesandordirs; Name: "{app}\data\.app-window"
Type: filesandordirs; Name: "{app}\data\.local"

[Code]
var
  MigratePage: TInputDirWizardPage;
  SetupResult: Integer;

function DefaultDir(Param: String): String;
begin
  if DirExists('E:\') then
    Result := 'E:\VoxViet Studio'
  else
    Result := ExpandConstant('{localappdata}\Programs\VoxViet Studio');
end;

procedure InitializeWizard;
begin
  SetupResult := -1;
  MigratePage := CreateInputDirPage(wpSelectDir,
    'Chuyển dữ liệu từ bản cũ',
    'Mang kho giọng, bản thu, từ điển, cài đặt và mô hình đã tải sang bản cài mới.',
    'Tìm thấy VoxViet Studio cài theo cách cũ (install.bat). Trình cài sẽ chép dữ liệu và CHUYỂN ' +
    'thư mục mô hình sang (không phải tải lại vài GB). Mã nguồn bản cũ giữ nguyên để bạn tự xoá sau.' + #13#10#13#10 +
    'Xoá trống ô dưới nếu không muốn chuyển.',
    False, '');
  MigratePage.Add('Thư mục bản cũ:');
  if FileExists(ExpandConstant('{#OldDefault}\app.py')) then
    MigratePage.Values[0] := '{#OldDefault}';
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := (PageID = MigratePage.ID) and (MigratePage.Values[0] = '');
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  Old: String;
begin
  Result := True;
  if CurPageID = MigratePage.ID then begin
    Old := Trim(MigratePage.Values[0]);
    if (Old <> '') and not FileExists(AddBackslash(Old) + 'app.py') then begin
      MsgBox('Thư mục này không phải bản VoxViet Studio cũ (không có app.py).', mbError, MB_OK);
      Result := False;
    end else if (Old <> '') and (CompareText(RemoveBackslash(Old), RemoveBackslash(WizardDirValue)) = 0) then begin
      MsgBox('Bản cũ trùng thư mục cài mới — hãy chọn thư mục cài khác, hoặc xoá trống ô này.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

function SetupOk: Boolean;
begin
  Result := SetupResult = 0;
end;

procedure RunSetupScript;
var
  Params, Old: String;
begin
  Old := Trim(MigratePage.Values[0]);
  Params := '-NoProfile -ExecutionPolicy Bypass -File "' + ExpandConstant('{app}\installer\setup.ps1') + '"';
  if Old <> '' then
    Params := Params + ' -MigrateFrom "' + RemoveBackslash(Old) + '"';
  // Kiểm thử tự động: /SKIPGIT=1 /CPUONLY=1
  if ExpandConstant('{param:SKIPGIT|0}') = '1' then Params := Params + ' -SkipGit';
  if ExpandConstant('{param:CPUONLY|0}') = '1' then Params := Params + ' -CpuOnly';
  if WizardSilent then Params := Params + ' -NoPause';
  WizardForm.StatusLabel.Caption := 'Đang cài Python, thư viện và nối GitHub (10–30 phút, xem cửa sổ PowerShell)…';
  WizardForm.ProgressGauge.Style := npbstMarquee;
  try
    if not Exec('powershell.exe', Params, ExpandConstant('{app}'), SW_SHOW, ewWaitUntilTerminated, SetupResult) then
      SetupResult := -1;
  finally
    WizardForm.ProgressGauge.Style := npbstNormal;
  end;
  Log('setup.ps1 exit code: ' + IntToStr(SetupResult));
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then begin
    RunSetupScript;
    while (SetupResult <> 0) and not WizardSilent do begin
      if MsgBox('Cài thư viện chưa xong (thường do mạng chập chờn).' + #13#10 +
                'Chi tiết: ' + ExpandConstant('{app}\data\.local\setup.log') + #13#10#13#10 +
                'Thử lại ngay?', mbError, MB_YESNO) = IDYES then
        RunSetupScript
      else begin
        MsgBox('Bạn có thể chạy lại sau bằng "VoxViet Studio - sửa bản cài" trong menu Start.', mbInformation, MB_OK);
        Break;
      end;
    end;
  end;
end;

// Cài thư viện lỗi → trình cài trả mã thoát 10 (để kiểm thử tự động phát hiện)
function GetCustomSetupExitCode: Integer;
begin
  if SetupResult <> 0 then Result := 10 else Result := 0;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  App: String;
begin
  if CurUninstallStep = usPostUninstall then begin
    App := ExpandConstant('{app}');
    if (not UninstallSilent) and
       (MsgBox('Xoá luôn kho giọng, bản thu, file đã đọc và mô hình đã tải?' + #13#10 +
               '(Chọn "No" để giữ lại — cài lại sau sẽ dùng tiếp.)', mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES) then begin
      DelTree(App + '\data', True, True, True);
      DelTree(App + '\models', True, True, True);
      DelTree(App, True, True, True);
    end;
  end;
end;
