"""Main module for the seismology data logger.

This module initializes and runs the data collection system.
"""

import datetime
import multiprocessing
import os
import threading
import time

from seismo import config, logging_utils

from . import ads_reader, data, gps, status_collector, web


def create_saver(report_type: str) -> data.BaseSaver:
    """Create a data saver instance based on the report type. Raises ValueError,
    if report_type is not supported
    """
    if report_type == "csv":
        return data.CSVSaver()
    raise ValueError(f"Unsupported report type: {report_type}")

def generate_report_filename(cfg: config.Config, current_sample: int) -> str:
    """Generate a filename for the data report, according to the format,
    specified in config.
    """
    timestamp = datetime.datetime.now(datetime.UTC).isoformat()

    filename = cfg.report_filename_format.format(
        timestamp=timestamp,
        number=current_sample,
    )
    return os.path.join(cfg.output_folder, filename)

if __name__ == "__main__":
    cfg = config.Config()
    logging_utils.setup_logging(cfg)
    logger = logging_utils.get_logger("SeismoLogger.main")

    if not os.path.exists(cfg.output_folder):
        try:
            os.makedirs(cfg.output_folder)
            logger.info(f"Created output folder: {cfg.output_folder}")
        except OSError as e:
            logger.error(f"Failed to create output folder {cfg.output_folder}: {e}")
            raise

    status_collector_instance = status_collector.StatusCollector(cfg)
    status_collector_instance.start()

    gps_reader = gps.GPSReader(cfg.gps, status_collector_instance)
    gps_thread = threading.Thread(
        target=gps_reader.gps_loop,
        name="GPSDaemon-1",
        daemon=True,
    )
    gps_thread.start()

    gps_reader.wait_for_gps()

    data_queue = data.DataQueue(data.CSVSaver(), cfg)

    if cfg.web_server.start_server:
        web_process = multiprocessing.Process(
            target=web.run_server,
            name="WebServerProcess",
            daemon=True,
        )
        web_process.start()

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
                    datetime.UTC).isoformat()

                data_batch = data_batch_template.get_copy_with_columns()

                start_perf = time.perf_counter()
                for _ in range(cfg.buffer_size):
                    sample = reader.read_channels_volts()
                    offset = time.perf_counter() - start_perf
                    data_batch.add_row_values([offset, sample[0]])

                data_queue.put(current_path, data_batch)

                current_gps = gps_reader.get_last_fix()
                meta_row = index_table.get_copy_with_columns()
                meta_row.add_row({
                    "start_time": start_iso,
                    "end_time": datetime.datetime.now(datetime.UTC)
                        .isoformat(),
                    "file_path": current_path,
                    "drate": cfg.ads.drate,
                    "sample_count": len(data_batch),
                    "latitude": current_gps["lat"],
                    "longitude": current_gps["lon"],
                    "altitude": current_gps["alt"],
                    "gps_satellites": current_gps["num_sats"],
                })

                data_queue.put(index_table_path, meta_row)

                if current_sample % 10 == 0:
                    logger.info(
                        f"Collected {current_sample} samples. "
                        f"Queue size: { len(data_queue) }",
                    )

                status_collector.update_status("queue_load", len(data_queue) / 20.0)
                status_collector.update_status(
                    "total_batches_saved", current_sample)
                status_collector.update_status(
                    "last_batch_time",
                    datetime.datetime.now(datetime.UTC).isoformat(),
                )

                current_sample += 1
    except KeyboardInterrupt:
        logger.info("Stopping data collection...")
    finally:
        logger.info("Waiting for pending save operations to complete...")
        data_queue.stop()
        logger.info("Done.")

