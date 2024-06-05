# stix2arango

stix2arango is a command line tool that takes a group of STIX 2.1 objects in a bundle and inserts them into ArangoDB. It can also handle updates to existing objects in ArangoDB imported in a bundle.

1. STIX 2.1 bundle entered
2. User chooses database/collection names (stix2arango creates as needed)
3. stix2arango inserts objects (or updates them) and then generates any relationships between them

## Usage

### Install the script

```shell
# clone the latest code
git clone https://github.com/muchdogesec/stix2arango
# create a venv
cd stix2arango
python3 -m venv stix2arango-venv
source stix2arango-venv/bin/activate
# install requirements
pip3 install -r requirements.txt
````

Note, the installation assumes ArangoDB is already installed locally.

[You can install ArangoDB here](https://arangodb.com/download/). stix2arango is compatible with both the Enterprise and Community versions.

#### A note for Mac users

Fellow Mac users, ArangoDB can be installed and run using homebrew as follows;

```shell
## Install
brew install arangodb
## Run
brew services start arangodb
## will now be accessible in a browser at: http://127.0.0.1:8529 . Default username is root with no password set (leave blank) 
## Stop
brew services stop arangodb
```

Sorry for the lack of other OS's -- I use a Mac.

### Setup configoration options

You will need to create an `.env` file as follows;

```shell
cp .env.example .env
```

You will then need to specify details of your ArangoDB install (host, user, and password). It is important the user chosen has the ability to write/update new databases, collections and records.

### Run

```shell
python3 stix2arango.py \
	--file PATH/TO/STIX.json \
	--database NAME \
	--collection NAME \
	--stix2arango_note SOMETHING
```

Where;

* `--file` (required): is the path to the valid STIX 2.1 bundle .json file
* `--database` (required): is the name of the Arango database the objects should be stored in. If database does not exist, stix2arango will create it
* `--collection` (required): is the name of the Arango collection in the database specified the objects should be stored in. If the collection does not exist, stix2arango will create it
* `--stix2arango_note` (optional): Will be stored under the `_stix2arango_note` custom attribute in ArangoDB. Useful as can be used in AQL. `a-z` characters only. Max 24 chars.
* `--ignore_embedded_relationships` (optional): boolean, if `true` passed, this will stop any embedded relationships from being generated. Default is `false`

For example, [using the MITRE ATT&CK Enterprise bundle](https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json);

```shell
python3 stix2arango.py \
	--file design/mvp/tests/enterprise-attack.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v14.1
```

However, if you didn't want to turn STIX embedded relationships as edges in the ArangoDB collection, you could use;

```shell
python3 stix2arango.py \
	--file design/mvp/tests/enterprise-attack.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v14.1 \
	--ignore_embedded_relationships true
```

#### A note on embedded relationships

stix2arango will handle all embedded references from properties found in the STIX 2.1 specification. It will also handle embedded references from MITRE ATT&CK and MITRE CAPEC.

The logic to identify these properties is hardcoded in `src/config.py` under the `refs_list` variable. You'll see a list of all supported property types embedded relationships are created from.

If you have your own STIX data with custom `_ref` or `_refs` properties you will need to add them to this list if you want stix2arango to generate embedded relationships from these, else they will be skipped.

## Quickstart

We store a lot of STIX data from popular knowledgebases in our repository [cti_knowledge_base_store](https://github.com/muchdogesec/cti_knowledge_base_store), along with scripts that can be used with stix2arango to import it.

This is useful to quickly populate STIX data using stix2arango if you want to see what it can do. It is also what is used to populate the data required by [arango_cti_processor](https://github.com/muchdogesec/arango_cti_processor/)

Here's how you can import that data...

```shell
git clone https://github.com/muchdogesec/cti_knowledge_base_store
cp cti_knowledge_base_store/utilities/stix2arango/insert_latest_data.sh insert_latest_data.sh
sh insert_latest_data.sh
```

## Useful supporting tools

* To generate STIX 2.1 Objects: [stix2 Python Lib](https://stix2.readthedocs.io/en/latest/)
* The STIX 2.1 specification: [STIX 2.1 docs](https://docs.oasis-open.org/cti/stix/v2.1/stix-v2.1.html)
* [ArangoDB docs](https://docs.arangodb.com/3.11/about-arangodb/)

## Support

[Minimal support provided via the DOGESEC community](https://community.dogesec.com/).

## License

[Apache 2.0](/LICENSE).