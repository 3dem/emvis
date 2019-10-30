
# Quick and dirty test script for TableModel class
# TODO: Improve it and use a proper test class

import os

import emcore as emc
import datavis as dv
import emvis as emv
from datavis.views import TableModel


testDataPath = os.environ.get("EM_TEST_DATA", None)

print("hasImpl('star'): ", emc.TableFile.hasImpl('star'))

if testDataPath is not None:
    # use the code below when yue have a properly configured environment
    fn1 = os.path.join(testDataPath, "relion_tutorial", "import", "refine3d",
                       "extra", "relion_it025_data.star")
    print("Reading star: ", fn1)

    t = emc.Table()
    tio = emc.TableFile()
    tio.open(fn1)
    tio.read("images", t)
    tio.close()

    refColNames = [
        "rlnVoltage", "rlnDefocusU", "rlnSphericalAberration",
        "rlnAmplitudeContrast", "rlnImageName", "rlnNormCorrection",
        "rlnMicrographName", "rlnGroupNumber", "rlnOriginX",
        "rlnOriginY", "rlnAngleRot", "rlnAngleTilt", "rlnAnglePsi",
        "rlnClassNumber", "rlnLogLikeliContribution",
        "rlnNrOfSignificantSamples", "rlnMaxValueProbDistribution"
    ]

    model = emv.models.ModelsFactory.createTableModel(fn1)
    tvc1 = dv.models.TableModel.fromTable(t)
    #print(tvc1)

    colsConfigs = [
        "rlnVoltage",
        "rlnDefocusU",
        "rlnSphericalAberration",
        "rlnAmplitudeContrast",
        ("rlnImageName", {'label': 'ImageName',
                          'renderable': True
                          })
    ]

    tvc2 = TableModel.fromTable(t, colsConfigs)
    print(tvc2)

