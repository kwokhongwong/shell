# Shell Black 76 Commodities Options Pricing Toy

## Assignment:
Implement a REST API web application for option pricing and market data storage

## Features:
1. Upload market data required for option pricing
2. Retrieve previously uploaded market data
3. Calculate PV of options with Black76 formula using previously uploaded market data

## Examples of options:
- BRENT Jan25 Call ATM
- BRENT Jan25 Call Strike 100 USD/BBL
- HH Mar24 Put Strike 10 USD/MMBTu

You have a freedom to choose technology stack, architecture, input/output schemas to best fit the requirements.

The code and design should meet these requirements, but be sufficiently flexible to allow future changes. The code should be well structured, commented, have error handling and be tested.
- Produce working, object-oriented source code.
- Provide as a GitHub project or send back in electronic format.
- We will walk through your code together in the next session, answering questions on the code and programming/design choices you made.
- At the interview you will be asked to present an end-to-end demo of the application.

## System Design / Architecture

The core system abstractions of interest are:
- System development process e.g. add new data, run alongside existing analytics etc
- Data storage of all types (market, reference/static, computed)
- Symbology/naming/discovery of all data types
- Daily/intraday processes
- Tooling to work in an agile manner, for all user types
- Core data and analytics data APIs/endpoints
- Testing to ensure/maintain quality
- Scalability considerations
- Time travel i.e. trade date vs market date (PIT)
- Any lambda architecture (intraday) is discussed lightly

### Client API

There exists a core interface for the supported client API i.e.

`api.BaseClient`

e.g. the following endpoints are of interest within this task
- `api.BaseClient.save(symbol, dataframe)` - used to save table data
- `api.BaseClient.data(symbol)` - query saved table data
- `api.BaseClient.commodity_option_price(...)` - Black 76 options pricer
- `api.BaseClient.commodity_option_greeks(...)` - Black 76 option greeks
- `api.BaseClient.option_price(...)` - GBS 73 options pricer
- `api.BaseClient.option_greeks(...)` - GBS 73 option greeks

2 implementations of `api.BaseClient` exist i.e.
- `api.LocalClient` for local/server use (used behind REST service)
- `api.RestClient` for local use, to compute using the server REST service

I have used Flask to implement the REST service given its simplicity
- Other frameworks exist e.g. Django, FastApi etc
- Marshmallow is used for basic validation/data schema

This design by interface is simple to extend, allowing abstraction/implementation of any other suitable wire transport
- For large data transfers arrow Flight might be considered (zero copy)

The following Jupyter Notebook demonstrates use the task goals
- `notebooks\Options Pricing.ipynb' (see .html output file)
- `notebooks\Market Data ETL.ipynb' (see .html output file)

Details of the Black 73 model implementation are explained in the options pricing notebook.

### Data Storage

A simple dedicated core API for persist/save exists
- `market.datastore_adapter.DataAPI'

and is accessible via these client API endpoints i.e. `save(...)` & `data(...)`

This simple design allows for easy data persist/query for adhoc data

Suitable for this toy implementation, data is stored to disk as parquet files
- It would be trivial to extend this to support any datastore 

A core part is symbology which has not been considered seriously here
- It would need to cover all data types (market, reference/static, analytics etc)
- This would be core for any data discovery
- A supporting DSL implementation (e.g. using EBNF/ANTLR)

## System Feature Extension / Expansion

More endpoints can be added to surface additional feature, in particular
- Develop more ETL adapters to munge/store additional datasets
- Expand the available client API endpoints
- Implement further analytics

The system design allows for 2 speed data munge/load i.e. casual users can munge/store adhoc data

## Automated Testing

Tests exist in the `tests' folder, covering
- market data ETL/save/query
- `RestClient` API (implicitly this tests `LocalClient`)
- analytics (including a simple benchmark option test)

pytest has been used given its simplicity and fast implementation.

## Scalability considerations

The technology choices used here are suitable as a toy example.

Evolving this further would require deeper alignment of data representation
- Storage
- Wire
- Memory format

Technologies aligned to arrow is worth serious consideration, alongside parallel scalable compute

Within `notebooks\Market Data ETL.ipynb' (see .html output file), `ray` is used for concurrent compute.

This is an important area in particular for large scale scenario/risk compute.

## Further Work / Considerations

Suitable design choices can be made to extend this basic implementation further:
- Use of intraday data / streaming event compute using `on_tick()` etc
- Development of a suitable SOD/EOD system data ETL scheduler e.g. luigi, Apache airflow etc
- Log record paradigm for true time travel (PIT) alongside trade_date/market_date
- Robust environment state management