import os 
import time
import datetime
import threading

from shared_modules import config
import shared_modules.logging_utils as logging_utils
from . import ads_reader
from . import data
from . import gps

def create_saver(report_type: str) -> data.BaseSaver:
    if report_type == "csv":
        return data.CSVSaver()
    else:
        raise ValueError(f"Unsupported report type: {report_type}")

def generate_report_filename(cfg: config.Config, current_sample: int) -> str:
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    filename = cfg.report_filename_format.format(
        timestamp=timestamp,
        number=current_sample
    )
    return os.path.join(cfg.output_folder, filename)

def main():
    cfg = config.Config()
    logging_utils.setup_logging(cfg)
    logger = logging_utils.get_logger("SeismoLogger.main")

    if not os.path.exists(cfg.output_folder):
        os.makedirs(cfg.output_folder)

    status_collector = status_collector.StatusCollector(cfg)
    status_collector.start()

    gps_i = gps.GPSReader(cfg.gps, status_collector)
    gps_thread = threading.Thread(
        target=gps_i.gps_loop, 
        name="GPSDaemon-1",
        daemon=True,
    )
    gps_thread.start()

    gps_i.wait_for_gps()

    saver = create_saver(cfg.report_type)
    dq = data.DataQueue(saver, cfg)

    index_table_path = os.path.join(cfg.output_folder, "reports_index.csv")
    index_table = data.DataTable()
    index_table.add_column("start_time", str)
    index_table.add_column("end_time", str)
    index_table.add_column("file_path", str)
    index_table.add_column("drate", int)
    index_table.add_column("sample_count", int)
    index_table.add_column("latitude", float)
    index_table.add_column("longitude", float)
    index_table.add_column("altitude", float)
    index_table.add_column("gps_satellites", int)

    data_batch_template = data.DataTable()

    logger.info(f"Starting data collection. Target SPS: { cfg.ads.drate }")

    try:
        current_sample = 1
        with ads_reader.ADSReader(cfg) as reader:
            while True:
                current_path = generate_report_filename(cfg, current_sample)
                start_iso = datetime.datetime.now(
                    datetime.timezone.utc).isoformat()

                data_batch = data_batch_template.get_copy_with_columns()

                start_perf = time.perf_counter()
                for _ in range(cfg.buffer_size):
                    sample = reader.read_channels_volts()
                    offset = time.perf_counter() - start_perf
                    data_batch.add_row_values([offset, sample[0]])

                dq.put(current_path, data_batch)

                current_gps = gps_i.get_last_fix()
                meta_row = index_table.get_copy_with_columns()
                meta_row.add_row({
                    "start_time": start_iso,
                    "end_time": datetime.datetime.now(datetime.timezone.utc)
                        .isoformat(),
                    "file_path": current_path,
                    "drate": cfg.ads.drate,
                    "sample_count": len(data_batch),
                    "latitude": current_gps["lat"],
                    "longitude": current_gps["lon"],
                    "altitude": current_gps["alt"],
                    "gps_satellites": current_gps["num_sats"]
                })

                dq.put(index_table_path, meta_row)

                if current_sample % 10 == 0:
                    logger.info(f"Collected {current_sample} samples. Queue size: { len(dq) }")

                status_collector.update_status("queue_load", len(dq) / 20.0)
                status_collector.update_status(
                    "total_batches_saved", current_sample)
                status_collector.update_status(
                    "last_batch_time", 
                    datetime.datetime.now(datetime.timezone.utc).isoformat()
                )

                current_sample += 1
    except KeyboardInterrupt:
        logger.info("Stopping data collection...")
    finally:
        logger.info("Waiting for pending save operations to complete...")
        dq.stop()
        logger.info("Done.")

