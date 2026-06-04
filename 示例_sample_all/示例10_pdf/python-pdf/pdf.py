from os.path import expanduser
import h5py
import numpy as np
import matplotlib.pyplot as plt
import logging
import sys
import os.path
import math
from colorama import Fore, Style
import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_pdf import PdfPages



# main variables
file_name = "C:\\Users\\richa\\Downloads\\data_log_files\\data_log_files\\data\\data0.hdf5"
reference = False  # set true if reference sensor involved
reference_siu_uuid = 2113171578
reference_port_num = 1 # port 0 is disabled msiu, set to whatevery port your reference device is on

# data processing options
use_baseline_segment = True
baseline_length = 12.5 # in seconds

# option to plot certain data
moving_average_plot = True # 10 sample moving average applied
absolute_position_plot = False # plots absolute position of all sensors
trim_bad_data_indicator = True # plots position with flagged bdi samples filtered out
trim_indicator = True # plots position with flagged indicator samples filtered out
remove_compensation_window_and_bad_data = True # removed 350ms of first 2 deviaitons for compensation window
                                               # of distorter start and distorter end


input_file_dir = os.path.dirname(file_name)
tracking_loss_event_log_output_filepath = os.path.join(input_file_dir, "tracking_loss_event_log.txt")
with open(tracking_loss_event_log_output_filepath, 'w') as f:
    pass

pdf_output_file_name = file_name[:file_name.rindex('\\')] + "\\" + 'all_plots_'+file_name[file_name.rindex('\\')+1:-5]+'.pdf'
pdf_out = PdfPages(pdf_output_file_name)

logging.getLogger('emc_analysis')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

data_file = h5py.File(expanduser(file_name), 'r')
test_regions = np.array([[0,-1]])
txt_file_name = file_name[:file_name.rindex('\\')] + "\\" + 'console_log_'+file_name[file_name.rindex('\\')+1:-5]+'.txt'
if os.path.isfile(txt_file_name):
    open(txt_file_name, 'w').close()
file_handler = logging.FileHandler(txt_file_name)
file_handler.setLevel(logging.INFO)


logger.addHandler(file_handler)

class LoggerWriter:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message and not message.isspace():
            self.logger.log(self.level, message.strip())

    def flush(self):
        pass  # This method is needed for compatibility with `sys.stdout`
sys.stdout = LoggerWriter(logger, logging.INFO)

pad_seconds = 5






def contiguous_regions(condition, min_len=0):
    """Finds contiguous True regions of the boolean array "condition". Returns
    a 2D array where the first column is the start index of the region and the
    second column is the end index."""

    # Find the indicies of changes in "condition"
    d = np.diff(condition)
    idx, = d.nonzero()

    # We need to start things after the change in "condition". Therefore,
    # we'll shift the index by 1 to the right.
    idx += 1

    if condition[0]:
        # If the start of condition is True prepend a 0
        idx = np.r_[0, idx]

    if condition[-1]:
        # If the end of condition is True, append the length of the array
        idx = np.r_[idx, condition.size] # Edit

    # Reshape the result into two columns
    idx.shape = (-1,2)
    idx = idx[np.subtract(idx[:, 1], idx[:, 0]) > min_len]
    return idx


def rolling_bidirection_diff(x, x_max = 0, axis=0):
    if axis != 0:
        raise NotImplementedError('')
    else:
        # escalate int typing to handle overflows
        type = np.int64 if np.issubdtype(x.dtype, np.integer) else np.double
        x_ax = np.array(x, dtype=type)

    diff = x_ax[1:] - x_ax[:-1]
    under = diff < (-x_max/2)
    over = diff > x_max/2
    return diff + under * x_max - over * x_max


def moving_average_3d(data, window_size):
    # Ensure the input is a 2D NumPy array with 3 columns for 3D coordinates
    data = np.array(data, dtype=float)

    # Apply the moving average separately for each dimension (x, y, z)
    x_smooth = np.convolve(data[:, 0], np.ones(window_size) / window_size, mode='valid')
    y_smooth = np.convolve(data[:, 1], np.ones(window_size) / window_size, mode='valid')
    z_smooth = np.convolve(data[:, 2], np.ones(window_size) / window_size, mode='valid')

    # Stack the smoothed x, y, z back into a 2D array again
    smoothed_data = np.stack((x_smooth, y_smooth, z_smooth), axis=-1)

    return smoothed_data


def downsample_average(data, chunk_size=1000):
    # Ensure the input is a 2D NumPy array with 3 columns for 3D coordinates
    data = np.array(data, dtype=float)

    # Calculate the number of complete chunks
    num_chunks = len(data) // chunk_size

    # Reshape each dimension separately, apply averaging for complete chunks
    x_avg = np.mean(data[:num_chunks * chunk_size, 0].reshape(-1, chunk_size), axis=1)
    y_avg = np.mean(data[:num_chunks * chunk_size, 1].reshape(-1, chunk_size), axis=1)
    z_avg = np.mean(data[:num_chunks * chunk_size, 2].reshape(-1, chunk_size), axis=1)

    # Handle any remaining points (the last incomplete chunk)
    if len(data) % chunk_size != 0:
        remainder_mean = np.mean(data[num_chunks * chunk_size:], axis=0)
        x_avg = np.append(x_avg, remainder_mean[0])
        y_avg = np.append(y_avg, remainder_mean[1])
        z_avg = np.append(z_avg, remainder_mean[2])

    # Stack the averaged x, y, z back into a 2D array
    downsampled_data = np.stack((x_avg, y_avg, z_avg), axis=-1)

    return downsampled_data


def downsample_dataframe(timestamp, datasets = [], target_hz=40):
    frame_size = 16000000/target_hz
    initial_timestamp = timestamp[0]
    last_frame = 1
    wrapped_dataframe = False
    new_datasets = [[] for i in datasets]
    new_timestamp = []

    for frame_idx in range(len(timestamp)):
        frame = timestamp[frame_idx]
        if frame < initial_timestamp:  # account for timestamp wrapping after maxing uint32
            initial_timestamp = frame
            last_frame = 1
            if frame + 4294967295 >= initial_timestamp + frame_size * last_frame:  # if wrapped frame is also dataframe value
                wrapped_dataframe = True
        if frame >= initial_timestamp + frame_size * last_frame or wrapped_dataframe:
            for dataset_idx in range(len(datasets)):
                dataset = datasets[dataset_idx]
                new_datasets[dataset_idx].append(dataset[frame_idx])
            new_timestamp.append(timestamp[frame_idx])
            if not wrapped_dataframe: last_frame = math.ceil((frame.item() - initial_timestamp.item())/frame_size)
            wrapped_dataframe = False
    return np.array(new_timestamp), [np.array(x) for x in new_datasets]

def moving_average_by_timestamp(data, timestamp, window_size = 0.25):
    moving_average_data = np.zeros_like(data)
    half_window = int(window_size * 16000000)
    unwrapped_timestamps = np.zeros_like(timestamp)
    offset = 0
    for frame in range(len(timestamp)):
        if timestamp[frame] < timestamp[frame-1]:
            offset += 2**32
        unwrapped_timestamps[frame] = timestamp[frame] + offset

    for frame in (range(len(timestamp))):
        current_time = timestamp[frame]
        start_time = current_time - half_window
        end_time = current_time + half_window
        # Efficiently find the indices for the start and end of the window
        start_idx = np.searchsorted(timestamp, start_time, side='left')
        end_idx = np.searchsorted(timestamp, end_time, side='right')
        # Get all position frames that fall within our time window
        window_positions = data[start_idx:end_idx]
        # Calculate the mean for the window and assign it
        if window_positions.shape[0] > 0:
            # axis=0 calculates the mean for each column (x, y, z) independently
            moving_average_data[frame] = np.mean(window_positions, axis=0)
        else:
            # If no other frames are in the window, just use the frame's own position
            moving_average_data[frame] = data[frame]
    return moving_average_data


def subtract_common_values(pos1, time1, pos2, time2, datasets = None):
    # find where timestamp is the same
    unwrapped_time1 = time1.copy()
    unwrapped_time2 = time2.copy()
    base_offset = 4294967295
    offset_count = 0
    common_timestamp_indicies = []
    for frame in range(len(unwrapped_time1)):
        if unwrapped_time1[frame] + base_offset * offset_count < unwrapped_time1[frame-1]:
            offset_count += 1
        offset = base_offset * offset_count
        unwrapped_time1[frame][0] = unwrapped_time1[frame][0] + offset
    offset_count = 0
    for frame in range(len(unwrapped_time2)):
        if unwrapped_time2[frame] + base_offset * offset_count < unwrapped_time2[frame-1]:
            offset_count += 1
        offset = base_offset * offset_count
        unwrapped_time2[frame][0] = unwrapped_time2[frame][0] + offset

    common_values, time1_indices, time2_indices = np.intersect1d( unwrapped_time1, unwrapped_time2, return_indices=True)
    common_pos1 = pos1[time1_indices]
    common_pos2 = pos2[time2_indices]
    for i in range(len(datasets)):
        dataset = np.array(datasets[i])
        datasets[i] = dataset[time2_indices]
    pos_difference = common_pos2 - common_pos1
    return pos_difference, datasets


def calculate_latency_metrics(
        samples,
        service_received,
        service_sent,
        target_p99_within,
        target_p100_within,
        target_p99_between,
        target_p100_data_age
):
    """
    Calculates key latency and stability metrics based on time-stamped packet data,
    comparing calculated percentiles against provided target thresholds.
    """

    S = np.array(samples)
    R = np.array(service_received)
    T = np.array(service_sent)

    min_len = min(len(S), len(R), len(T))
    max_len = max(len(S), len(R), len(T))
    print("timestamp packets dropped for latency calculations: " + str(max_len - min_len))
    if min_len < 2:
        return {"error": "Need at least 2 packets to calculate all metrics."}

    S = S[:min_len]
    T = T[:min_len]


    # Calculate Latency Distributions
    # Time within a packet: service_sent[n] - sample[n]
    time_within_packet = T - S

    # Time between packets: service_sent[n+1] - service_sent[n]
    time_between_packets = T[1:] - T[:-1]

    # Data Age: service_sent[n+1] - sample[n]
    data_age = T[1:] - S[:-1]

    results = {}

    p99_within = np.percentile(time_within_packet, 99)
    p100_within = np.max(time_within_packet)
    results['time_within_packet_p99_ms'] = round(p99_within, 3)
    results['time_within_packet_p100_ms'] = round(p100_within, 3)
    results['time_within_packet_p99_status'] = "PASS" if p99_within <= target_p99_within else "FAILED"
    results['time_within_packet_p100_status'] = "PASS" if p100_within <= target_p100_within else "FAILED"

    p99_between = np.percentile(time_between_packets, 99)
    results['time_between_packets_p99_ms'] = round(p99_between, 3)
    results['time_between_packets_p99_status'] = "PASS" if p99_between <= target_p99_between else "FAILED"

    p100_data_age = np.max(data_age)
    results['data_age_p100_ms'] = round(p100_data_age, 3)
    results['data_age_p100_status'] = "PASS" if p100_data_age <= target_p100_data_age else "FAILED"
    return results


def count_long_sections_above_threshold(numbers, timestamps, threshold=1, duration_units=16000000):
    above_threshold = numbers > threshold
    if not np.any(above_threshold):
        return 0
    # Find the change points in the boolean mask
    diff = np.diff(above_threshold.astype(int))
    # Get start indices (+1 transition)
    start_indices = np.where(diff == 1)[0] + 1
    # Get end indices (-1 transition). These are exclusive (index *after* the section)
    end_indices = np.where(diff == -1)[0] + 1
    # Handle section starting at the beginning
    if above_threshold[0]:
        start_indices = np.insert(start_indices, 0, 0)
    # Handle section ending at the end
    if above_threshold[-1]:
        end_indices = np.append(end_indices, len(numbers))
    if len(start_indices) != len(end_indices):
        return 0
    durations = timestamps[end_indices - 1] - timestamps[start_indices]
    # Count sections longer than the required duration
    long_sections_count = np.sum(durations > duration_units)
    return long_sections_count





def process_device(device, t0, time_segments:np.ndarray, reference_sensor):
    logging.info(f' device:{device.name}')

    timestamp_full = device['Timestamp']
    # timestamp_full, _ = downsample_dataframe(timestamp_full)

    timestamp_delta = rolling_bidirection_diff(timestamp_full, 4294967296)
    time_passed = np.insert(timestamp_delta, 0, (timestamp_full[0, 0] - t0))
    # same length of original timestamp, starting from t0 across all devices
    time_passed = np.cumsum(time_passed)
    print('start time={} end time={} samples={}'.format(time_passed[0] / 16000000.0, time_passed[-1] / 16000000.0,
          np.shape(timestamp_full)[0]))
    for row in range(np.shape(time_segments)[0]):
        start_clock = max((time_segments[row,0] - pad_seconds) * 16000000.0, 0)
        end_clock = time_passed[-1]
        if time_segments[row, 1] > 0 and time_segments[row, 1] > time_segments[row, 0]:
            end_clock = min((time_segments[row,1] + pad_seconds) * 16000000.0, time_passed[-1])
        start_idx = np.where(time_passed >= start_clock)[0][0]
        end_idx = np.where(time_passed >= end_clock)[0][0] + 1
        delta_start_idx = max(start_idx - 1, 0)
        delta_end_idx = end_idx - 1

        timestamp = time_passed[start_idx:end_idx,...]#[20000:]
        timestamp_raw = device["Timestamp"][start_idx:end_idx,...]
        encoder = device['Theta'][start_idx:end_idx,...]#[20000:]
        indicator = device['Indicator'][start_idx:end_idx,...]#[20000:]
        position = device['Position'][start_idx:end_idx,...]#[20000:]
        mag = device['Mag'][start_idx:end_idx,...]#[20000:]
        if 'BadDataIndicator' in device: bad_data_indicator = device["BadDataIndicator"][start_idx:end_idx, ...]
        elif trim_bad_data_indicator or remove_compensation_window_and_bad_data: messagebox.showerror("Error", "Bad data indicator not in file. Unselect option")
        if "LatencyTimestamp_Sample" in device and "LatencyTimestamp_ServiceReceived" in device and "LatencyTimestamp_ServiceSent" in device:
            latencytimestamp_sample = device["LatencyTimestamp_Sample"][start_idx:end_idx,...]
            latencytimestamp_servicereceived = device["LatencyTimestamp_ServiceReceived"][start_idx:end_idx,...]
            latencytimestamp_servicesent = device["LatencyTimestamp_ServiceSent"][start_idx:end_idx,...]
        else: print("No latency datasets in file, skipping latency metrics")

        print(np.shape(timestamp), np.shape(encoder), np.shape(position))


        #downsample to 40hz
        encoder = [x[0] for x in encoder]
        indicator = [x[0] for x in indicator]
        indicator = [x[0] for x in indicator]
        position = [x[0] for x in position]

        encoder_delta = rolling_bidirection_diff(np.array(encoder), 3600)
        #  duplicate last encoder delta value to keep dataset same length as timestamp
        encoder_delta = np.append(encoder_delta, encoder_delta[-1])

        global_position = np.array(position)
        global_timestamp = np.array(timestamp)
        global_indicator = np.array(indicator)
        global_bad_data_indicator = np.array(indicator)

        if reference_sensor["is_active"]:
            if int(device.name[-1]) == reference_sensor["index_in_siu"] and int(device.name[-11:-2]) == int(str(reference_sensor["siu_uuid"])[-9:]):
                reference_sensor["position"] = np.array(position)
                reference_sensor["timestamp"] = np.array(timestamp_raw, dtype=np.int64)
            else:
                position, [encoder, indicator, timestamp, mag, bad_data_indicator, encoder_delta] = subtract_common_values(reference_sensor["position"], reference_sensor["timestamp"], np.array(position), np.array(timestamp_raw, dtype=np.int64), [encoder, indicator, timestamp, mag, bad_data_indicator, encoder_delta])
        # subtract using timestamps
            # make position only the indices where timestamps match, then subtract

        global_timestamp_downsampled, [global_position_downsampled, global_indicator_downsampled, global_bad_data_indicator_downsampled] = downsample_dataframe(global_timestamp, [global_position, global_indicator, global_bad_data_indicator])
        timestamp_downsampled, [encoder_downsampled, indicator_downsampled, position_downsampled, mag_downsampled, bad_data_indicator_downsampled, encoder_delta_downsampled] = downsample_dataframe(timestamp, [encoder, indicator,  position, mag, bad_data_indicator, encoder_delta])
        timestamp, encoder, indicator, position, mag, bad_data_indicator, encoder_delta = np.array(timestamp), np.array(encoder), np.array(indicator), np.array(position), np.array(mag), np.array(bad_data_indicator), np.array(encoder_delta)
        # timestamp, [encoder, indicator, position, mag, bad_data_indicator] = np.array(timestamp), [np.array(encoder), np.array(indicator), np.array(position), np.array(mag), np.array(bad_data_indicator)]



        # smooth position and splice it into chunks of 1000
        smoothed_position = moving_average_3d(position, 20)
        smoothed_position_downsampled = moving_average_3d(position_downsampled, 20)
        downsampled_position = downsample_average(smoothed_position, 200)
        downsampled_position_downsampled = downsample_average(smoothed_position_downsampled, 200)
        position_delta_vector = downsampled_position[-1]-downsampled_position[0]
        position_delta_magnitude = np.linalg.norm(downsampled_position[0]-downsampled_position[-1])
        print("position delta vector = " + str(position_delta_vector), "position delta magnitude = " + str(position_delta_magnitude))

        # check timestamp
        delta = timestamp_delta[delta_start_idx:delta_end_idx,...]
        delta_values, delta_counts = np.unique(delta, return_counts=True)
        ts_events = np.logical_or(delta < 15980*25, delta > 10 * 15980*25)
        ts_event_idx = np.where(ts_events)[0]
        # don't add 1 to index, this gives us the timestamp at the beginning of the event
        # (next sample generates the event)
        try:
            ts_events_s = timestamp[ts_event_idx] / 16000000.0
            logging.info(f'Timestamp events:{ts_events_s}')
            logging.info(f'Timestamp events packets loss:{delta[ts_event_idx].flatten()/(15984*25)}')
        except Exception as e: print(e)

        if use_baseline_segment:
            ts_units = baseline_length * 16000000
            start_time = timestamp_downsampled[0]
            end_time = start_time + ts_units
            global_positions_to_average = [global_position_downsampled[i] for i in range(len(timestamp_downsampled)) if timestamp_downsampled[i] <= end_time]
            global_average_position = sum(global_positions_to_average) / len(global_positions_to_average)
            reference_positions_to_average = [position_downsampled[i] for i in range(len(timestamp_downsampled)) if timestamp_downsampled[i] <= end_time]
            reference_average_position = sum(reference_positions_to_average) / len(reference_positions_to_average)
        else:
            global_average_position = global_position_downsampled[0, :]
            reference_average_position = position_downsampled[0, :]


        position_centered = position[:, :] - position[0, :]
        position_centered_downsampled = position_downsampled[:, :] - reference_average_position
        global_position_centered_downsampled = global_position_downsampled[:, :] - global_average_position
        position_centered_magnitude = np.array( [math.sqrt(x[0] ** 2 + x[1] ** 2 + x[2] ** 2) for x in position_centered])
        position_centered_magnitude_downsampled = np.array([math.sqrt(x[0] ** 2 + x[1] ** 2 + x[2] ** 2) for x in position_centered_downsampled])
        downsampled_position_centered = downsampled_position - position[0, :]
        downsampled_position_centered_downsampled = downsampled_position - position[0, :]




        # post processing
        # thresholds ----
        indicator_threshold = 0.5 # set to >=1 if you do not want to trim any high indicator data
        compensation_window = math.ceil(350 / 25) # 350ms / 25ms (size of each sample in 40hz)
        region_threshold = 2 # max regions that can fall under compensation window
        # ----
        tests_failed = 0
        tests_failed_color = Fore.GREEN
        mixed_indicator_downsampled = indicator_downsampled[np.squeeze(bad_data_indicator_downsampled) < 1]
        global_mixed_indicator_downsampled = indicator_downsampled[np.squeeze(global_bad_data_indicator_downsampled) < 1]
        position_centered_low_indicator = position_centered_downsampled[global_bad_data_indicator_downsampled < indicator_threshold]
        global_position_centered_low_indicator = global_position_centered_downsampled[global_mixed_indicator_downsampled < indicator_threshold]
        timestamp_low_indicator = timestamp_downsampled[indicator_downsampled < indicator_threshold]
        global_timestamp_low_indicator = global_timestamp_downsampled[global_indicator_downsampled < indicator_threshold]
        moving_average_position_downsampled = moving_average_by_timestamp(position_centered_low_indicator, timestamp_low_indicator)
        global_moving_average_position_downsampled = moving_average_by_timestamp(global_position_centered_low_indicator, global_timestamp_low_indicator)
        moving_average_position_magnitude = np.array([math.sqrt(x[0]**2+x[1]**2+x[2]**2) for x in moving_average_position_downsampled]) ###
        global_moving_average_position_magnitude = np.array([math.sqrt(x[0]**2+x[1]**2+x[2]**2) for x in global_moving_average_position_downsampled])
        timestamp_delta_low_indicator = rolling_bidirection_diff(timestamp_low_indicator, 4294967296)
        moving_average_position_with_indicator = moving_average_by_timestamp(position_centered_downsampled, timestamp_downsampled)
        moving_average_position_with_indicator_magnitude = np.array([math.sqrt(x[0]**2+x[1]**2+x[2]**2) for x in moving_average_position_with_indicator])
        indicator_not_bad_position = indicator_downsampled[moving_average_position_with_indicator_magnitude <1]
        tracking_loss_event_log = {}

        print("METRICS:")
        print("USING BASELINE OF FIRST " + str(baseline_length) + " seconds" )
        if int(device.name[-1]) == reference_sensor["index_in_siu"] and int(device.name[-11:-2]) == int(str(reference_sensor["siu_uuid"])[-9:]):
            print(f"{Fore.WHITE}" + "REFERENCE DEVICE" + f"{Style.RESET_ALL}")
        else: print(f"{Fore.WHITE}" + "TRACKING DEVICE" + f"{Style.RESET_ALL}")

        # indicator value <10% triggered test
        if (indicator_downsampled > indicator_threshold).mean() <= 0.1: indicator_pass = "PASS"; color = Fore.GREEN  # check if 90% of indicator value is less than threshold
        else: indicator_pass = "FAIL"; color = Fore.YELLOW; tests_failed +=1; tests_failed_color = Fore.YELLOW
        print(f"{color}" + indicator_pass + ": 90% of data without indicator value test: " +f"{Style.RESET_ALL}"+ str((indicator_downsampled > indicator_threshold).mean()*100) + "% of samples triggered indicator value")

        #data loss tests
        if np.sum(timestamp_delta_low_indicator >= 32000000) > 0: two_second_data_loss = "FAIL"; color = Fore.YELLOW; tests_failed +=1; tests_failed_color = Fore.YELLOW  # if we lose tracking for more than 2s at all
        else: two_second_data_loss = "PASS"; color = Fore.GREEN
        tracking_loss_event_log["two_second_data_loss"] = np.where(timestamp_delta_low_indicator >= 32000000)
        print(f"{color}" + two_second_data_loss + ": 2-second tracking loss test (allowed: 0 instances): " + f"{Style.RESET_ALL}" + str(np.sum(timestamp_delta >= 32000000)) + " instances of 2 second data loss")

        if np.sum(timestamp_delta_low_indicator >= 420000) > 1: two_packets_data_loss = "FAIL"; color = Fore.YELLOW; tests_failed +=1; tests_failed_color = Fore.YELLOW # if we lost more than one packet
        else: two_packets_data_loss = "PASS"; color = Fore.GREEN
        tracking_loss_event_log["any_data_loss"] = np.where(timestamp_delta_low_indicator >= 420000)
        print(f"{color}" + two_packets_data_loss + ": any-duration tracking loss test (allowed: 1 instance): " + f"{Style.RESET_ALL}" + str(np.sum(timestamp_delta_low_indicator >= 420000)) + " instances of data loss")
        accumulated_time_loss = timestamp_delta_low_indicator[timestamp_delta_low_indicator > 420000].sum()
        if global_moving_average_position_magnitude.size == 0:
            print(f"{Fore.WHITE}" + "Accumulated loss of tracking time: FAIL: all data thrown out by indicator value")
        else:
            print(f"{Fore.WHITE}" + "Accumulated loss of tracking time: " + str(accumulated_time_loss/16000000) + "s = " + f"{accumulated_time_loss/timestamp_low_indicator[-1]*100:.3f}" + "% of test time " + f"{timestamp_low_indicator[-1]/16000000:.3f}" + "s" + f"{Style.RESET_ALL}")

        # global 99% and 95% accuracy test
        if global_moving_average_position_magnitude.size == 0:
            print(""f"{Fore.YELLOW}" + "FAIL" + ": 99% global accuracy test (threshold 1mm): " +f"{Style.RESET_ALL}"+ "all data thrown out by indicator value")
        else:
            global99 = np.sort(global_moving_average_position_magnitude)[math.floor(len(global_moving_average_position_magnitude)*99/100)]
            if (global_moving_average_position_magnitude < 1).mean() >= 0.99: moving_average_99_pass = "PASS"; color = Fore.GREEN
            else: moving_average_99_pass = "FAIL"; color = Fore.YELLOW; tests_failed += 1; tests_failed_color = Fore.YELLOW
            print(f"{color}" + moving_average_99_pass + ": 99% global accuracy test (threshold 1mm): " +f"{Style.RESET_ALL}"+ str((global_moving_average_position_magnitude < 1).mean()*100) + "% of data passing accuracy. 99% acc is " + str(global99) + "mm")
            if (global_moving_average_position_magnitude < 1).mean() >= 0.95: moving_average_95_pass = "PASS"; color = Fore.GREEN
            else: moving_average_95_pass = "FAIL"; color = Fore.YELLOW; tests_failed += 1; tests_failed_color = Fore.YELLOW
            print(f"{color}" + moving_average_95_pass + ": 95% global accuracy test (threshold 1mm): " +f"{Style.RESET_ALL}"+ str((global_moving_average_position_magnitude < 1).mean()*100) + "% of data passing accuracy. 95% acc is " + str(np.sort(global_moving_average_position_magnitude)[math.floor(len(global_moving_average_position_magnitude)*95/100)]) + "mm")

         # reference 99% and 95% accuracy test
        if reference_sensor["is_active"]:
            if not (int(device.name[-1]) == reference_sensor["index_in_siu"] and int(device.name[-11:-2]) == int(str(reference_sensor["siu_uuid"])[-9:])):
                 if moving_average_position_magnitude.size == 0:
                    print(""f"{Fore.YELLOW}" + "FAIL" + ": 99% accuracy test (threshold 1mm): " +f"{Style.RESET_ALL}"+ "all data thrown out by indicator value")
                 else:

                    ref99 = np.sort(moving_average_position_magnitude)[math.floor(len(moving_average_position_magnitude)*99/100)]
                    if (moving_average_position_magnitude < 1).mean() >= 0.99: moving_average_99_pass = "PASS"; color = Fore.GREEN
                    else: moving_average_99_pass = "FAIL"; color = Fore.YELLOW; tests_failed += 1; tests_failed_color = Fore.YELLOW
                    print(f"{color}" + moving_average_99_pass + ": 99% reference accuracy test (threshold 1mm): " +f"{Style.RESET_ALL}"+ str((moving_average_position_magnitude < 1).mean()*100) + "% of data passing accuracy. 99% acc is " + str(ref99) + "mm")
                    if (moving_average_position_magnitude < 1).mean() >= 0.95: moving_average_95_pass = "PASS"; color = Fore.GREEN
                    else: moving_average_95_pass = "FAIL"; color = Fore.YELLOW; tests_failed += 1; tests_failed_color = Fore.YELLOW
                    print(f"{color}" + moving_average_95_pass + ": 95% reference accuracy test (threshold 1mm): " +f"{Style.RESET_ALL}"+ str((moving_average_position_magnitude < 1).mean()*100) + "% of data passing accuracy. 95% acc is " + str(np.sort(moving_average_position_magnitude)[math.floor(len(moving_average_position_magnitude)*95/100)]) + "mm")
                    print(f"{Fore.WHITE}" + "DELTA||V|| P99 (99%ref - 99%global): " + str(ref99 - global99) + " mm" +f"{Style.RESET_ALL}")

        # indicator value false negative test (1%) (is exact same as accuracy test)
        if moving_average_position_magnitude.size == 0:
            print(""f"{Fore.YELLOW}" + "FAIL" + ": indicator value false negative test (threshold 1%): " +f"{Style.RESET_ALL}"+ "all data thrown out by indicator value")
        else:
            if (moving_average_position_magnitude < 1).mean() >= 0.99: indicator_false_negative = "PASS"; color = Fore.GREEN
            else: indicator_false_negative = "FAIL"; color = Fore.YELLOW; tests_failed +=1; tests_failed_color = Fore.YELLOW
            print(f"{color}" + indicator_false_negative + ": indicator value false negative test (threshold 1%): " +f"{Style.RESET_ALL}"+ str((moving_average_position_magnitude > 1).mean()*100) + "% (" + str((moving_average_position_magnitude > 1).sum()) + " samples) false negative rate (1mm deviation not caught by indicator)")
            count_false_negative_over_1s = count_long_sections_above_threshold(moving_average_position_magnitude, timestamp_low_indicator)
            print(f"{Fore.WHITE}" + str(count_false_negative_over_1s) + " groups where false negative for >1s" + f"{Style.RESET_ALL}")

        # indicator value fase positive test (10%) (will only fail if 90% of data not triggering indicator also fails
        if (indicator_not_bad_position > indicator_threshold).mean() <= 0.9: indicator_false_positive = "PASS"; color = Fore.GREEN  # check if 90% of indicator value is less than threshold
        else: indicator_false_positive = "FAIL"; color = Fore.YELLOW; tests_failed +=1; tests_failed_color = Fore.YELLOW
        print(f"{color}" + indicator_false_positive + ": indicator value false positive test (threshold 10%): " +f"{Style.RESET_ALL}"+ str((indicator_not_bad_position > indicator_threshold).mean()*100) + "% false positive rate (0.1 indicator value with no 1mm deviation)")

        # latency metrics
        if "LatencyTimestamp_Sample" in device and "LatencyTimestamp_ServiceReceived" in device and "LatencyTimestamp_ServiceSent" in device:
            TARGETS = {'p99_time_within': 50.0,  'p100_time_within': 150.0, 'p99_time_between': 50.0,   'p100_data_age': 150.0}
            latency_results = calculate_latency_metrics( latencytimestamp_sample, latencytimestamp_servicereceived, latencytimestamp_servicesent,TARGETS['p99_time_within'],TARGETS['p100_time_within'],TARGETS['p99_time_between'],TARGETS['p100_data_age'] )
            print(f"{Fore.WHITE}" + "--- Latency Metrics ---")
            print(f"Total packets analyzed: { min(len(latencytimestamp_sample), len(latencytimestamp_servicereceived), len(latencytimestamp_servicesent))}")
            print(f"Time Within Packet (Target P99: {TARGETS['p99_time_within']}ms):")
            print(f"Calculated P99: {latency_results['time_within_packet_p99_ms']:.3f} ms -> {latency_results['time_within_packet_p99_status']}")
            print(f"Calculated P100 (Max): {latency_results['time_within_packet_p100_ms']:.3f} ms (Target 150ms) -> {latency_results['time_within_packet_p100_status']}")
            print(f"Time Between Packets (Target P99: {TARGETS['p99_time_between']}ms):")
            print( f"Calculated P99: {latency_results['time_between_packets_p99_ms']:.3f} ms -> {latency_results['time_between_packets_p99_status']}")
            print(f"Data Age (Target P100: {TARGETS['p100_data_age']}ms):")
            print( f"Calculated P100 (Max): {latency_results['data_age_p100_ms']:.3f} ms -> {latency_results['data_age_p100_status']}" +f"{Style.RESET_ALL}")

        print(f"{tests_failed_color}" + ("tests failed: " + str(tests_failed) + f"{Style.RESET_ALL}"))


        regions = contiguous_regions(np.abs(position_centered_magnitude) > 1, 5)
        regions_five_mm = contiguous_regions(np.abs(position_centered_magnitude) > 5, 2)
        print("start_position={}".format(position[0, :]))
        logging.info(f' position over +/-1mm:{regions}')
        num_regions = np.shape(regions)[0]
        num_regions_five_mm = np.shape(regions_five_mm)[0]


        if num_regions > 0:
            fig, ax = plt.subplots(num_regions + 1, 1, figsize = (10, 8))
            fig.tight_layout(pad=3)
            fig.suptitle('device={} time={} regions'.format(device.name, time_segments[row]))
            mask = np.ones(np.shape(position_centered)[0], dtype=bool)
            for i in range(num_regions):
                region_end_idx = regions[i,1]
                if region_end_idx >= np.shape(position_centered)[0]:
                    region_end_idx = np.shape(position_centered)[0]-1
                logging.info(f'Region start={timestamp[regions[i,0]] / 16000000.0} end={timestamp[region_end_idx] / 16000000.0}')
                mask[regions[i,0]:regions[i,1]] = False
                ax[i].plot(position_centered[regions[i,0]:regions[i,1]],'.', rasterized=True)
                ax[i].title.set_text("Region of Deviation >+/-1mm "+str(i)); ax[i].set_xlabel("Samples"); ax[i].set_ylabel("Deviation (mm)")
            ax[num_regions].plot(position_centered[mask],'.', rasterized=True)
            ax[num_regions].title.set_text("Dataset with >+/-1mm Deviations Removed"); ax[num_regions].set_xlabel("Samples"); ax[num_regions].set_ylabel("Deviation (mm)")
            # fig.savefig(file_name[:file_name.rindex('\\')] + "\\" + 'deviations_' + device.name[1:] +'_'+file_name[file_name.rindex('\\')+1:-5]+ '.png')
            pdf_out.savefig(fig)
            plt.close(fig)

        #  default fig
        numrows = 4
        if max(delta) > 160000: numrows += 1
        if absolute_position_plot: numrows += 1
        if 'BadDataIndicator' in device: numrows += 1
        fig, ax = plt.subplots(numrows, 1, figsize=(10, 8))
        fig.tight_layout(pad=3)
        fig.suptitle('DEFAULT device={} time={}'.format(device.name, time_segments[row]))
        index = 0
        ax[index].plot(delta, '.', rasterized=True)
        ax[index].title.set_text("Timestamp Deltas");
        bottom, auto_top = ax[index].get_ylim()
        # ax[index].set_ylim(bottom=bottom, top=min(auto_top, 160000))
        ax[index].set_xlabel("Samples");
        ax[index].set_ylabel("Delta Between Timestamps")
        index += 1

        if max(delta) > 160000:
            ax[index].plot(delta, '.', rasterized=True)
            ax[index].title.set_text("Timestamp Deltas ymax 10 samples");
            bottom, auto_top = ax[index].get_ylim()
            ax[index].set_ylim(bottom=bottom, top=min(auto_top, 160000))
            ax[index].set_xlabel("Samples");
            ax[index].set_ylabel("Delta Between Timestamps")
            index += 1

        logging.info(f' Timestamp deltas:{delta_values}\n counts:{delta_counts}')

        # delta = rolling_bidirection_diff(encoder, 3600)
        delta_values, delta_counts = np.unique(encoder_delta, return_counts=True)
        encoder_events = np.logical_or(encoder_delta < 0, encoder_delta > 1500)
        encoder_events_idx = np.where(encoder_events)[0]
        # don't add 1 to index, this gives us the timestamp at the beginning of the event
        # (next sample generates the event)
        encoder_events_s = timestamp[encoder_events_idx] / 16000000.0
        logging.info(f'Encoder events:{encoder_events_s}')

        ax[index].plot(encoder_delta, '.', rasterized=True)
        ax[index].title.set_text("Encoder Deltas");
        ax[index].set_xlabel("Samples");
        ax[index].set_ylabel("Delta Between Encoder Measurments")
        logging.info(f' Encoder deltas:{delta_values}\n counts:{delta_counts}')
        index += 1
        ax[index].plot(position_centered, '.', rasterized=True)
        ax[index].plot(np.linspace(0, len(position_centered) - 1, len(downsampled_position_centered)),
                   downsampled_position_centered, linewidth=4)
        ax[index].title.set_text("Position Change");
        ax[index].set_xlabel("Samples");
        ax[index].set_ylabel("Position from origin (mm)");
        ax[index].legend(['x', 'y', 'z', 'x filtered', 'y filtered', 'z filtered'], loc='right')
        index += 1
        if absolute_position_plot:
            ax[index].plot(position[:, :], '.', rasterized=True)
            ax[index].title.set_text("Absolute Position");
            ax[index].set_xlabel("Samples");
            ax[index].set_ylabel("Position from Base Station (mm)")
            index += 1
        ax[index].plot(indicator[:], '.', rasterized=True)
        ax[index].title.set_text("Indicator");
        ax[index].set_xlabel("Samples");
        ax[index].set_ylabel("Indicator value")
        index += 1
        # if len(mag[:, :]) > 500:
        #     ax[5].plot(range(math.floor(len(mag[:, :])/2)-250,math.floor(len(mag[:, :])/2)+250),mag[:, 0][math.floor(len(mag[:, 0])/2)-250:math.floor(len(mag[:, 0])/2)+250], '.')
        #     ax[5].title.set_text("Mag"); ax[5].set_xlabel("Samples"); ax[5].set_ylabel("Mag value")
        if 'BadDataIndicator' in device and trim_bad_data_indicator:
            indices_to_keep = bad_data_indicator[:, 0, 0] <= 0.5
            bad_data_trimmed_position = position[indices_to_keep, :]
            bad_indicator_trimmed_position_centered = bad_data_trimmed_position[:, :] - bad_data_trimmed_position[0, :]
            ax[index].plot(bad_data_indicator[:, 0, :], '.', rasterized=True)
            ax[index].title.set_text("Bad Data Indicator");
            ax[index].set_xlabel("Samples");
            ax[index].set_ylabel("Bad data indicator value")
            index += 1
        pdf_out.savefig(fig)
        plt.close(fig)

        numrows = 0
        if 'BadDataIndicator' in device and trim_bad_data_indicator: numrows += 1
        if trim_indicator and len(position[(indicator[:] <= indicator_threshold), :]) > 0: numrows += 1
        if remove_compensation_window_and_bad_data: numrows += 2
        fig, ax = plt.subplots(numrows, 1, figsize=(10, 8))
        ax = np.atleast_1d(ax)
        fig.tight_layout(pad=3)
        fig.suptitle('DEFAULT PAGE 2 device={} time={}'.format(device.name, time_segments[row]))
        index = 0
        if 'BadDataIndicator' in device and trim_bad_data_indicator:
            ax[index].plot(bad_indicator_trimmed_position_centered, '.', rasterized=True)
            ax[index].title.set_text("Bad Data Trimmed Position Change");
            ax[index].set_xlabel("Samples");
            ax[index].set_ylabel("Bad data trimmed position change")
            index += 1
        if remove_compensation_window_and_bad_data:
            if num_regions > 0:
                mask = np.ones(np.shape(position_centered)[0], dtype=bool)
                regions_trimmed = 0
                for i in range(num_regions):
                    halt = True
                    for j in range(num_regions_five_mm):
                        if regions_five_mm[j,0] >= regions[i,0] and regions_five_mm[j,1] <= regions[i,1]: halt = False
                    if regions_trimmed > region_threshold or halt: continue
                    region_end_idx = regions[i, 1]
                    if regions[i,1] - regions[i,0] > compensation_window:
                        mask[regions[i, 0]:regions[i, 0] + compensation_window] = False
                    else:  mask[regions[i,0]:regions[i,1]] = False
                    regions_trimmed += 1
                bad_data_masked = bad_data_indicator[mask]
                position_masked = position[mask]
                if trim_bad_data_indicator and 'BadDataIndicator' in device:
                    indices_to_keep = bad_data_masked[:, 0, 0] <= 0.5
                    bad_data_trimmed_position_regions = position_masked[indices_to_keep, :]
                    bad_data_trimmed_position_regions_centered = bad_data_trimmed_position_regions[:, :] - bad_data_trimmed_position_regions[0, :]
                ax[index].plot(bad_data_trimmed_position_regions_centered, '.', rasterized=True)
                ax[index].title.set_text("Position with 350ms of first 2 >+/-1mm Deviations and bad data Removed");
                ax[index].set_xlabel("Samples");
                ax[index].set_ylabel("Deviation (mm)")
                index += 1

            if num_regions > 0:
                mask = np.ones(np.shape(position_centered)[0], dtype=bool)
                regions_trimmed = 0
                for i in range(num_regions):
                    halt = True
                    for j in range(num_regions_five_mm):
                        if regions_five_mm[j,0] >= regions[i,0] and regions_five_mm[j,1] <= regions[i,1]: halt = False
                    if regions_trimmed > region_threshold or halt: continue
                    region_end_idx = regions[i, 1]
                    if regions[i, 1] - regions[i, 0] > compensation_window:
                        mask[regions[i, 0]:regions[i, 0] + compensation_window] = False
                    else:
                        mask[regions[i, 0]:regions[i, 1]] = False
                    regions_trimmed += 1
                ax[index].plot(position_centered[mask], '.', rasterized=True)
                ax[index].title.set_text("Position with 350ms of first 2 >+/-1mm Deviations Removed");
                ax[index].set_xlabel("Samples");
                ax[index].set_ylabel("Deviation (mm)")
                index += 1

        if trim_indicator and len(position[(indicator[:] <= indicator_threshold), :]) >0:
            indices_to_keep = indicator[:] <= indicator_threshold
            indicator_trimmed_position = position[indices_to_keep, :]
            indicator_trimmed_position_centered = indicator_trimmed_position[:, :] - indicator_trimmed_position[0, :]
            ax[index].plot(indicator_trimmed_position_centered[:, :], '.', rasterized=True)
            ax[index].title.set_text("Indicator " + str(indicator_threshold) +  " Trimmed Position Change");
            ax[index].set_xlabel("Samples")
            ax[index].set_ylabel("Indicator trimmed position change")
            index += 1
        # fig.savefig(file_name[:file_name.rindex('\\')] + "\\" + 'default_output_' + device.name[1:] + '_' + file_name[file_name.rindex('\\') + 1:-5] + '.png')
        pdf_out.savefig(fig)
        plt.close(fig)

        #  brainlab fig
        numrows = 4
        if absolute_position_plot: numrows += 1
        if 'BadDataIndicator' in device: numrows += 2
        if trim_indicator and len(position_downsampled[(indicator_downsampled[:] <= indicator_threshold), :]) > 0: numrows += 1
        if moving_average_position_downsampled.size > 0 and moving_average_plot: numrows += 1
        fig, ax = plt.subplots(numrows, 1, figsize=(10, 8))
        fig.tight_layout(pad=3)
        fig.suptitle('BRAINLAB device={} time={}'.format(device.name, time_segments[row]))
        index = 0
        #add all things downsampled

        ax[index].plot(delta, '.', rasterized=True)
        ax[index].title.set_text("Timestamp Deltas");
        bottom, auto_top = ax[index].get_ylim()
        # ax[index].set_ylim(bottom=bottom, top=min(auto_top, 160000))
        ax[index].set_xlabel("Samples");
        ax[index].set_ylabel("Delta Between Timestamps")
        index += 1

        delta_values, delta_counts = np.unique(encoder_delta_downsampled, return_counts=True)
        encoder_events = np.logical_or(encoder_delta_downsampled < 0, encoder_delta_downsampled > 1500)
        encoder_events_idx = np.where(encoder_events)[0]
        encoder_events_s = timestamp_downsampled[encoder_events_idx] / 16000000.0
        ax[index].plot(encoder_delta_downsampled, '.', rasterized=True)
        ax[index].title.set_text("Encoder Deltas");
        ax[index].set_xlabel("Samples");
        ax[index].set_ylabel("Delta Between Encoder Measurments")
        logging.info(f' Encoder deltas:{delta_values}\n counts:{delta_counts}')
        index += 1

        ax[index].plot(position_centered_downsampled, '.', rasterized=True)
        ax[index].plot(np.linspace(0, len(position_centered_downsampled) - 1, len(downsampled_position_centered_downsampled)),downsampled_position_centered_downsampled, linewidth=4)
        ax[index].title.set_text("Position Change");
        ax[index].set_xlabel("Samples");
        ax[index].set_ylabel("Position from origin (mm)");
        ax[index].legend(['x', 'y', 'z', 'x filtered', 'y filtered', 'z filtered'], loc='right')
        index += 1

        ax[index].plot(indicator_downsampled[:], '.', rasterized=True)
        ax[index].title.set_text("Indicator");
        ax[index].set_xlabel("Samples");
        ax[index].set_ylabel("Indicator value")
        index += 1

        if 'BadDataIndicator' in device:
            if trim_bad_data_indicator and 'BadDataIndicator' in device:
                indices_to_keep = bad_data_indicator_downsampled[:, 0, 0] <= 0.5
                bad_data_trimmed_position = position_downsampled[indices_to_keep, :]
            elif trim_bad_data_indicator:
                print("failed to trim bad indicator value: dataset not in file")
            bad_indicator_trimmed_position_centered = bad_data_trimmed_position[:, :] - bad_data_trimmed_position[0, :]
            ax[index].plot(bad_data_indicator_downsampled[:, 0, :], '.', rasterized=True)
            ax[index].title.set_text("Bad Data Indicator");
            ax[index].set_xlabel("Samples");
            ax[index].set_ylabel("Bad data indicator value")
            index += 1
            ax[index].plot(bad_indicator_trimmed_position_centered, '.', rasterized=True)
            ax[index].title.set_text("Bad Data Trimmed Position Change");
            ax[index].set_xlabel("Samples");
            ax[index].set_ylabel("Bad data trimmed position change")
            index += 1

            if trim_indicator and len(position_downsampled[(indicator_downsampled[:] <= indicator_threshold), :]) > 0:
                indices_to_keep = indicator_downsampled[:] <= indicator_threshold
                indicator_trimmed_position = position_downsampled[indices_to_keep, :]
                indicator_trimmed_position_centered = indicator_trimmed_position[:, :] - indicator_trimmed_position[0,:]
                ax[index].plot(indicator_trimmed_position_centered[:, :], '.', rasterized=True)
                ax[index].title.set_text("Indicator " + str(indicator_threshold) + " Trimmed Position Change");
                ax[index].set_xlabel("Samples")
                ax[index].set_ylabel("Indicator trimmed position change")
                index += 1

        if moving_average_position_downsampled.size > 0 and moving_average_plot:
            ax[index].plot(moving_average_position_downsampled, rasterized=True)
            ax[index].title.set_text("Brainlab Downsampled -- Moving Average -- Indicator Trimmed < " + str(indicator_threshold) + " -- Position Change");
            ax[index].set_xlabel("Samples");
            ax[index].set_ylabel("Position from origin (mm)");
            ax[index].legend(['x', 'y', 'z', 'x filtered', 'y filtered', 'z filtered'], loc='right')
            index += 1


        # fig.savefig(file_name[:file_name.rindex('\\')] + "\\" + 'brainlab_output_' + device.name[1:] + '_' + file_name[file_name.rindex('\\') + 1:-5] + '.png')
        pdf_out.savefig(fig)
        plt.close(fig)

        #plt.show()

        device_type = "Measurement"
        if reference_sensor["is_active"]:
            if (int(device.name[-1]) == reference_sensor["index_in_siu"] and int(device.name[-11:-2]) == int(str(reference_sensor["siu_uuid"])[-9:])):
                device_type = "Reference"
        with open(tracking_loss_event_log_output_filepath, 'a') as f:
            f.write("\n========================================\n")
            f.write("--- Tracking Loss Event Log ---\n\n")
            f.write(device_type + "\n")
            f.write(f"Source Data Length: {len(timestamp_delta_low_indicator)} samples\n\n")

            # Iterate through the dictionary to write each event
            for event_name, indices_array in tracking_loss_event_log.items():
                f.write(f"Event: {event_name}\n")
                f.write(f"Count: {len(indices_array)}\n")

                # Convert the NumPy index array to a comma-separated string for easy reading
                indices_str = ', '.join(map(str, indices_array))
                f.write(f"Indices: [{indices_str}]\n\n")

        print(f"Successfully wrote tracking log data to: tracking_loss_event_log.txt")


def process_file(file:h5py.File, test_regions):
    logging.info(f'file={file.filename}')
    logging.info(f'devices={file.keys()}')

    t0_all = []
    for device in file.values():
        if 'Timestamp' in device:
            t0_all.append(device['Timestamp'][0,0])

    t0_all = np.array(t0_all, dtype=np.int64)
    t0 = np.min(t0_all)
    t0_idx = np.where(t0_all==t0)[0]
    logging.info(f' t0_all={t0_all} t0={t0} t0_device_idx={t0_idx}')

    reference_sensor = {
        "is_active": reference,
        "siu_uuid": None,
        "index_in_siu": None,
        "position": np.empty(0),
        "timestamp": np.empty(0)
    }

    reference_sensor["siu_uuid"], reference_sensor["index_in_siu"] = reference_siu_uuid, reference_port_num

    for device in file.values():
        if 'Timestamp' in device:
            if int(device.name[-1]) == reference_sensor["index_in_siu"] and int(device.name[-11:-2]) == int(str(reference_sensor["siu_uuid"])[-9:]) and "Position" in device and "Mag" in device:
                process_device(device, t0, test_regions, reference_sensor)

    for device in file.values():
        if 'Timestamp' in device:
            if int(device.name[-1]) == reference_sensor["index_in_siu"] and int(device.name[-11:-2]) == int(str(reference_sensor["siu_uuid"])[-9:]) and "Position" in device:
                pass
            elif "Position" in device and "Mag" in device:
                process_device(device, t0, test_regions, reference_sensor)

def main():
    process_file(data_file, test_regions)
    pdf_out.close()
    sys.stdout.flush()

if __name__ == "__main__":
    main()