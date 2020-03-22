import requests
import csv
import os

'''
Format: 
Each market is a folder labeled with ID -- i.e. market2721
contains: 
A. "2721_meta.csv"
| "id", "name", "shortName", "image", "status", "url"  #only one
| "id", "name", "shortName", "image", "status", "dateEnd"  # for each contract
|
2. "contract4390.csv"
| "timeStamp", "lastTradePrice", "bestBuyYesCost", "bestBuyNoCost", "bestSellYesCost", "bestSellNoCost", "lastClosePrice"
|
Each contract file (i.e. 4390.csv)
'''

def should_update_prices(new_prices, prev_prices, diff=0.01):
    try:
        prev_prices = [0 if (i == '' or i == '\n') else float(i) for i in prev_prices]
        new_prices = [0 if i == None else i for i in new_prices]
    except:
        print("hello")
        return True

    update_prices = False
    for i in range(0, len(new_prices) - 1):
        if abs(new_prices[i] - prev_prices[i]) > diff:
            update_prices = True

    return update_prices


def get_latest_data(dest="data/", marketFileKey="id", contractFileKey="id"):
    response = requests.get("https://www.predictit.org/api/marketdata/all/")

    data = response.json()
    markets = data['markets']

    NUMBER_UPDATED = 0
    TOTAL_CONTRACTS = 0

    for market in markets:
        marketDir = dest + "market" + str(market[marketFileKey])
        if not os.path.exists(marketDir):
            os.makedirs(marketDir)

        if os.path.exists(marketDir + "/" + str(market[marketFileKey]) + "_meta.csv"):
            doesMetaExist = True
        else:
            doesMetaExist = False

        with open(marketDir + "/" + str(market[marketFileKey]) + "_meta.csv", "a") as meta_file:
            meta_writer = csv.writer(meta_file, delimiter=",")
            if not doesMetaExist:
                meta_writer.writerow(["id", "name", "shortName", "image", "status", "url"])
                meta_writer.writerow(
                    [market["id"], market["name"], market["shortName"], market["image"], market["status"],
                     market["url"]])
                meta_writer.writerow(["id", "name", "shortName", "image", "status", "dateEnd"])

            for contract in market["contracts"]:
                TOTAL_CONTRACTS += 1

                if not doesMetaExist:
                    meta_writer.writerow(
                        [contract["id"], contract["name"], contract["shortName"], contract["image"], contract["status"],
                         contract["dateEnd"]])

                if os.path.exists(marketDir + "/contract" + str(contract[contractFileKey]) + ".csv"):
                    doesContractExist = True

                    with open(marketDir + "/contract_last" + str(contract[contractFileKey]) + ".csv", "r") as last_record_read:
                        last_record = [i for i in last_record_read.readline().split(",")]

                    last_record_read.close()

                else:
                    doesContractExist = False

                with open(marketDir + "/contract" + str(contract[contractFileKey]) + ".csv", "a") as contract_file:
                    contract_writer = csv.writer(contract_file, delimiter=",")

                    timeStamp = market["timeStamp"]
                    curr_prices = [contract["bestBuyYesCost"], contract["bestBuyNoCost"], contract["bestSellYesCost"], contract["bestSellNoCost"]]

                    if not doesContractExist:
                        contract_writer.writerow(["timeStamp", "bestBuyYesCost", "bestBuyNoCost", "bestSellYesCost", "bestSellNoCost"])
                        contract_writer.writerow([timeStamp] + curr_prices)

                    else:
                        update_prices = should_update_prices(curr_prices, last_record)

                        if update_prices:
                            NUMBER_UPDATED += 1
                            contract_writer.writerow([timeStamp] + curr_prices)

                if (not doesContractExist) or update_prices:
                    with open(marketDir + "/contract_last" + str(contract[contractFileKey]) + ".csv", "w") as last_record_write:
                        last_writer = csv.writer(last_record_write, delimiter=",")

                        last_writer.writerow(curr_prices)

                contract_file.close()
        meta_file.close()

get_latest_data(dest="data/")
