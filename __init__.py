import rigBuilder
from maya import cmds


@rigBuilder.clock
def build_mgear(guide_path):
    print(guide_path)

    import mgear.shifter.io
    mgear.shifter.io.build_from_file(filePath=guide_path)


@rigBuilder.clock
def import_ctrls_shapes(path):
    print(path)

    import ctrlShaper
    if ctrlShaper.NurbsCurvesFile.is_one(path):
        ctrlShaper.NurbsCurvesFile(path).load()
    else:
        cmds.warning('\'{0}\' is not a valid.'.format(path))