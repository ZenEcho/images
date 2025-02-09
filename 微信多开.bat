@echo off
setlocal enabledelayedexpansion

:loop
cls
echo ------------微信多开脚本------------
echo 脚本用于解决微信不能多开的问题
echo By：智通技术部 V：1.0.0
echo ---------------------------------------

rem 查找当前目录下快捷方式中的路径
set A=微信
set Z=.lnk
set "A=%A%%Z%"

rem 检查快捷方式是否存在并提取目标路径
for /f "tokens=* usebackq" %%i in (`type "%A%" ^| find "\" ^| findstr /b "[a-z][:][\\]"`) do (
    set _targetdir=%%~dpi
)

rem 如果快捷方式路径存在，直接使用该路径
if defined _targetdir (
    set "exe_path=!_targetdir!\WeChat.exe"
) else (
    rem 提示用户输入exe文件路径
    set /p exe_path=输入程序路径or拖拽到此: 
    rem 去掉路径中的双引号
    set "exe_path=!exe_path:"=!"
)

rem 提示用户输入打开次数
set /p open_times=打开次数: 

rem 循环打开exe文件
for /l %%i in (1,1,!open_times!) do (
    start "" "!exe_path!"
)

goto loop
