
DEFINES = \
{
    "TXMODE": True,
    "DEBUG": False,
}

# DEFINES = {
#     "TXMODE": False,
#     "DEBUG": True,
# }


def defined(macro_name):
    is_defined = macro_name in DEFINES
    is_enabled = DEFINES[macro_name]
    return is_defined and is_enabled


if defined("TXMODE"):
    print("tx")

elif defined("DEBUG"):
    print("debug")
else:
    print("默认模式执行")

