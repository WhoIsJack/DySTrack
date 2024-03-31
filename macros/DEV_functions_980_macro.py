###TEST
## reuse settings
hardwaresetting1 = ZenHardwareSetting()
hardwaresetting1.SetParameter('MTBLKM980Laser561', 'IsEnabled', 'true')
Zen.Devices.ApplyHardwareSetting(hardwaresetting1)



hardwaresetting1.SetParameter('MTBLSM880PinholeDiameter', 'Position', '312.83')
Zen.Devices.ApplyHardwareSetting(hardwaresetting1)

hardwaresetting1.SetParameter('MTBLKM980Laser561', 'IsEnabled', 'true')
Zen.Devices.ApplyHardwareSetting(hardwaresetting1)

###Live


experiment1 = Zen.Acquisition.Experiments.GetByName("LSM 3 colors_Blue, Green, Red.czexp")
Zen.Acquisition.StartLive(experiment1)
liveimage1 = Zen.Application.Documents.GetByName("C:\Users\zeiss\Pictures\temp\Live.czi")
liveimage1.Graphics.HideGrid()
Zen.Acquisition.StopLive(experiment1)

###Set Z (current position/from last position)

# CAUTION! Risk of Crushing when executing code!
Zen.Devices.Focus.TargetPosition = 6339.55
Zen.Devices.Focus.Apply()

# CAUTION! Risk of Crushing when executing code!
Zen.Devices.Focus.TargetPosition = -303.15
Zen.Devices.Focus.Apply()

# CAUTION! Risk of Crushing when executing code!
Zen.Devices.Focus.TargetPosition = 0
Zen.Devices.Focus.Apply()

hardwaresetting1.SetParameter('MTBLKM980Laser561', 'IsEnabled', 'true')
Zen.Devices.ApplyHardwareSetting(hardwaresetting1)

###Set X Y position

Zen.Acquisition.StartLive(experiment1)
liveimage1.Graphics.HideGrid()
Zen.Devices.Stage.TargetPositionX = 62912.68
Zen.Devices.Stage.Apply()
Zen.Devices.Stage.TargetPositionY = 32349.23
Zen.Devices.Stage.Apply()


Zen.Acquisition.StopLive(experiment1)


###Start acquisition

outputexperiment1 = Zen.Acquisition.Execute(experiment1)
# *************** End of Code Block *****************