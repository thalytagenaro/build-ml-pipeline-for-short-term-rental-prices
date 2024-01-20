#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    logger.info("Initializing wandb run")
    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    logger.info(f"Reading artifact: {args.input_artifact}")
    input_artifact_path = wandb.use_artifact(args.input_artifact).file()
    df = pd.read_csv(input_artifact_path)

    logger.info(f"Removing outliers - setting price between {args.min_price} and {args.max_price}")
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()

    logger.info("Converting date column 'last_review' type")
    df['last_review'] = pd.to_datetime(df['last_review'])

    logger.info("Saving results")
    df.to_csv(args.output_artifact, index=False)

    logger.info("Logging artifact to W&B") 
    artifact = wandb.Artifact(
        name=args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file(args.output_artifact)

    run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Input artifact (.csv file)",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Name for the output artifact",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="Type for the output artifact",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Description for the output artifact",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Minimum price to consider",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Maximum price to consider",
        required=True
    )


    args = parser.parse_args()

    go(args)
