@echo off
setlocal enabledelayedexpansion

:loop
cls
echo ------------΢�Ŷ࿪�ű�------------
echo �ű����ڽ��΢�Ų��ܶ࿪������
echo By����ͨ������ V��1.0.0
echo ---------------------------------------

rem ���ҵ�ǰĿ¼�¿�ݷ�ʽ�е�·��
set A=΢��
set Z=.lnk
set "A=%A%%Z%"

rem ����ݷ�ʽ�Ƿ���ڲ���ȡĿ��·��
for /f "tokens=* usebackq" %%i in (`type "%A%" ^| find "\" ^| findstr /b "[a-z][:][\\]"`) do (
    set _targetdir=%%~dpi
)

rem �����ݷ�ʽ·�����ڣ�ֱ��ʹ�ø�·��
if defined _targetdir (
    set "exe_path=!_targetdir!\WeChat.exe"
) else (
    rem ��ʾ�û�����exe�ļ�·��
    set /p exe_path=�������·��or��ק����: 
    rem ȥ��·���е�˫����
    set "exe_path=!exe_path:"=!"
)

rem ��ʾ�û�����򿪴���
set /p open_times=�򿪴���: 

rem ѭ����exe�ļ�
for /l %%i in (1,1,!open_times!) do (
    start "" "!exe_path!"
)

goto loop
