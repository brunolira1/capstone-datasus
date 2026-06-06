import pyarrow.parquet as pq

def concat_parquets_low_mem(file_paths, columns, output_path):
    writer = None

    for path in file_paths:
        parquet_file = pq.ParquetFile(path)

        for i in range(parquet_file.num_row_groups):
            table = parquet_file.read_row_group(i, columns=columns)

            if writer is None:
                writer = pq.ParquetWriter(output_path, table.schema)

            writer.write_table(table)

    if writer:
        writer.close()

    return output_path