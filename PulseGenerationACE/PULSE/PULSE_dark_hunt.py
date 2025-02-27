import numpy as np
from matplotlib import pyplot as plt
from scipy.io import savemat
import pyaceqd.pulsegenerator as pg 
import os as os
from Pulse_v2 import fake_spectrometer, fake_motor, pulse_shaper_obj, simulator, attenuator, half_wave_plate, fake_attenuator, motor, spectrometer, load_pulse_device, create_experiment, save_pulse, save_temp, save_device, excecute_folder, power_meter, time_delay, fake_power_meter, generic_wave_plate

import initialPulse_control as ip
import control_optimizer as con_opt
import hyper_dimensional_scan as hds
import initialPulse_control as ip
from PULSE_gui_tools import gui_manager

import sys

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

#blockPrint()

cur_dir = os.getcwd()
if 'PulseGenerationACE' in cur_dir:
    pass
else:
# change the directory to the folder where the calibration files are stored
    os.chdir(cur_dir+'/PulseGenerationACE/PULSE')
print(cur_dir) 

ps_calibration = 'calibration_slit_13.txt' 
#ps_calibration2 = 'calibration_slit_38.txt' 
qd_calibration = 'QD_Iker_April.txt'

lab_motor = motor(fake_motor(),name='motor1')
lab_att = fake_attenuator()
lab_spectromter = fake_spectrometer(start_wl=774.15, end_wl = 793.422, n_wl = 1340)

lab_motor2 = motor(fake_motor(),name='motor2')
lab_motor3 = motor(fake_motor(),name='motor3')
lab_motor4 = motor(fake_motor(),name='motor4')
lab_motor5 = motor(fake_motor(),name='motor5')
lab_motor6 = motor(fake_motor(),name='motor6')
lab_motor7 = motor(fake_motor(),name='motor7')
lab_motor8 = motor(fake_motor(),name='motor8')

lab_att2 = fake_attenuator()

t_0 = 0 
t_end = 50
dt = 0.2


###### set 1 +45 ps^2
chirp_1 = 45 #45
chirp_2 = 45 #45
ps_A = 778.909
att_B = 0.174
ps_C = 777.8
att_D = 0.724
delay_F = -32.038 
dipole = 3.5

###### set 2 - / + 45 ps^2
chirp_1 = -45 #45
chirp_2 = +45 #45
ps_A = 778.909
att_B = 0.174
ps_C = 777.8
att_D = 0.724
delay_F = -32.038 
dipole = 3.5

###### set 2 + / - 45 ps^2
chirp_1 = 0 #45
chirp_2 = -0 #-45
ps_A = 780.8#778.909
att_B = 0.5#0# 0.622
ps_C = 780.8#780.8 #777.961
att_D = 0.5
delay_F = 0 #-90 
dipole = 1


initial_pulse = pg.PulseGenerator(t_0,t_end,dt,calibration_file=qd_calibration)
initial_pulse.add_gaussian_time(unit = 'nm', central_f= 779, width_t=0.1,t0=t_end/2,area_time=20, polarisation=[0,1])

initial_pulse2 = initial_pulse.copy_pulse()

initial_pulse.add_filter_rectangle()
initial_pulse.add_phase_filter(unit='nm', phase_taylor=[0,0,chirp_1],central_f=780.8)
#initial_pulse.add_filter_double_erf(unit='nm', central_f=779.89, width_f=0.35, rise_f=0.1, invert=True,merging='*')
#initial_pulse.add_filter_double_erf(unit='nm', central_f=781.79, width_f=0.35, rise_f=0.1, invert=True,merging='*')
initial_pulse.apply_frequency_filter()

initial_pulse2.add_filter_rectangle()
initial_pulse2.add_phase_filter(unit='nm', phase_taylor=[0,0,chirp_2],central_f=780.8)
#initial_pulse2.add_filter_double_erf(unit='nm', central_f=779.89, width_f=0.35, rise_f=0.1, invert=True,merging='*')
#initial_pulse2.add_filter_double_erf(unit='nm', central_f=781.79, width_f=0.35, rise_f=0.1, invert=True,merging='*')
initial_pulse2.apply_frequency_filter()

ipA_control = ip.Pulse_Generator(initial_pulse = initial_pulse, name='initial_pulse_A')
ipB_control = ip.Pulse_Generator(initial_pulse = initial_pulse2, name='initial_pulse_B')

hwp_1 = generic_wave_plate(device=lab_motor4, name='A: HWP')
qwp_1 = generic_wave_plate(device=lab_motor5, name='A: QWP',phase=np.pi/2)
pulse_shaper = pulse_shaper_obj(device=lab_motor, calibration_file=ps_calibration, name='A: Pulse shaper')
delay_A = time_delay(device=lab_motor6, name='A: Delay stage')
att_object = attenuator(lab_att, name = 'A: Attenuator')

hwp_2 = generic_wave_plate(device=lab_motor7, name='B: HWP')
qwp_2 = generic_wave_plate(device=lab_motor8, name='B: QWP',phase=np.pi/2)
pulse_shaper2 = pulse_shaper_obj(device=lab_motor2, calibration_file=ps_calibration, name='B: Pulse shaper2')
att_object2 = attenuator(lab_att, name = 'B: Attenuator2')

delay_stage = time_delay(device=lab_motor3, name='B: Delay stage')


hwp_1_controller = hwp_1.open_control(previous_control=ipA_control)
qwp_1_controller = qwp_1.open_control(previous_control=hwp_1_controller)
ps_controller = pulse_shaper.open_control(previous_control=qwp_1_controller)
del_controller = delay_A.open_control(previous_control=ps_controller)
att_controller = att_object.open_control(previous_control=del_controller)

ps_controller.set_control_value(ps_A)
att_controller.set_control_value(att_B)

hwp_2_controller = hwp_2.open_control(previous_control=ipB_control)
qwp_2_controller = qwp_2.open_control(previous_control=hwp_2_controller)
ps_controller2 = pulse_shaper2.open_control(previous_control=qwp_2_controller)
att_controller2 = att_object2.open_control(previous_control=ps_controller2)

ps_controller2.set_control_value(ps_C)
att_controller2.set_control_value(att_D)

delay_controller = delay_stage.open_control(previous_control=att_controller2)
delay_controller.set_control_value(delay_F)


simulator_object = simulator(qd_calibration=qd_calibration, sim_kind='ace_6ls', temp_dir='sim_dump/')
simulator_object.set_ace_six_level(b_x=3.4,b_z = 0, b_field_frame=True)
sim_controller = simulator_object.open_control(previous_control = [att_controller,delay_controller],open_gui=False) #,delay_controller
sim_controller.set_dipole_moment(dipole)
sim_controller.gui()

spec = spectrometer(device=lab_spectromter, name='MF_spec') 
sm_controller = spec.open_control(pulse_object=None,previous_control = [att_controller,delay_controller], simulation_control= sim_controller,open_gui=False) #, ps_controller3#ps_controller2.get_pulse_object()
sm_controller.set_simulation_background(0)
sm_controller.set_simulation_gaussian_noise(0)#4.35

sm_controller.set_simulation_counts(500)
#sm_controller.toggle_running()
sm_controller.change_view()
sm_controller.gui()

#sim_controller.toggle_running()
#sim_controller.update_gui()

#sm_controller.update_gui()

power_meter_M2 = power_meter(fake_power_meter(),name='A: power_meter')
power_meter_M2_control = power_meter_M2.open_control(previous_control=[att_controller],open_gui=True)

power_meter_M3 = power_meter(fake_power_meter(),name='B: power_meter')
power_meter_M3_control = power_meter_M3.open_control(previous_control=[delay_controller],open_gui=True)

power_meter_M4 = power_meter(fake_power_meter(),name='AB: power_meter')
power_meter_M4_control = power_meter_M4.open_control(previous_control=[att_controller,delay_controller],open_gui=True)

device_list = [ps_controller,att_controller, ps_controller2,att_controller2,delay_controller,hwp_1_controller,qwp_1_controller,hwp_2_controller,qwp_2_controller]

co = con_opt.control_optimizer(device_control=device_list,measururement_control=sm_controller,measurement_kind='spectrometer',open_gui=False) # ,delay_controller , ps_controller,att_controller
co.set_scan_limits([(778.8,779.2),(0.01,1), (777.8,778.2),(0.01,1), (0,20)]) #,(-10,10) ,(778.8,779.2),(0.01,1)
sm_controller.set_measurement_method('multi line', arg=2)
sm_controller.set_measurement_arguments(arguments=[2,781.79, 0.01, 'max','',781.79, 0.01, 'max','']) # dark 779.95
#co.set_spectrometer_measurement(779.95,0.01,method='max')
co.gui()

scan = hds.hyper_scan(device_control=[ps_controller,att_controller, ps_controller2,att_controller2,delay_controller,hwp_1_controller,qwp_1_controller,hwp_2_controller, qwp_2_controller],measururement_control=[sm_controller, power_meter_M2_control, power_meter_M3_control,power_meter_M4_control],open_gui=True) #, ps_controller,att_controller

gui_m = gui_manager(device_control=[ipA_control,ipB_control,ps_controller,att_controller,del_controller, ps_controller2,att_controller2,delay_controller, sm_controller, sim_controller,hwp_1_controller, qwp_1_controller, hwp_2_controller, qwp_2_controller,power_meter_M2_control, power_meter_M3_control,power_meter_M4_control, co, scan],num_coloums=2)
#co.run_optimization()
sm_controller.start_gui()