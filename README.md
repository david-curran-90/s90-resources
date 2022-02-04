# s90-resourcess

List resource usage alongside requests and limits. This view should give a good infication as to how well the reource requests/limits are set

This plugin replaces a far more complicated set of commands with a nicer output

## Installation

**Written using Python 3.8.5, will require python >=3.6 to run**

* From Source

Get the repo and move the file into place

```
git clone https://github.com/schizoid90/s90-resources.git
mkdir -r ~/.krew/store/s90-resources/0.1.0/
mv kubectl-s90-resources/src/* ~/.krew/store/s90-resources/0.1.0/
chmod +x ~/.krew/store/s90-resources/0.1.0/
```

## Usage

```
kubectl s90-resourcess -n {namespace}
```

Resource information will be printed in a table. Output is colour coded, if usage is below 90% of requested it will appear in red, otherwise in green.

```
+-----------+--------------------------+---------------+-------------+------------------+--------------+----------+---------------+-----------+
| Namespace |           Pod            |   Container   | Memory Used | Memory Requested | Memory Limit | CPU used | CPU Requested | CPU Limit |
+-----------+--------------------------+---------------+-------------+------------------+--------------+----------+---------------+-----------+
|  traefik  | traefik-79c97b9b54-zrv89 |    traefik    |   50.84Mi   |       50Mi       |    150Mi     |    4m    |      100m     |    300m   |
|  traefik  | traefik-79c97b9b54-zrv89 | linkerd-proxy |   24.61Mi   |       none       |     none     |    1m    |      none     |    none   |
+-----------+--------------------------+---------------+-------------+------------------+--------------+----------+---------------+-----------+
```

To only show containers that fall below 90% usage of the requested resource use `--show-lowusage`. Edit the threshold to report low usage on (defualt 30%) with `-t {int}`

### Options

```
kubectl s90-resourcess -h
usage: kubectl-s90-resourcess [-h] [--version] [--namespace NS] [--debug]
                           [--show-lowusage] [--threshold THRESHOLD]

Show decoded secrets information

optional arguments:
  -h, --help            show this help message and exit
  --version, -v         show program's version number and exit
  --namespace NS, -n NS
                        Set namespace
  --debug, -d           Print debug information
  --show-lowusage       Only show containers with lower usage than requested
  --threshold THRESHOLD, -t THRESHOLD
                        percent of requested resources used to alert on 
```

## Limitations

### --all-namespace

Currenlty this command must be namespaced so the `-A` or `--all-namespaces` flags cannot be used

### Yes debug IS info

If logging is set to debug then we get loads of info from the kubernetes module. So debug = info

## TODO

* run against all namespacecs
* specify a pod/container
* exclude pods/containers
* output to different methods (e.g. csv)
* offer proper debug option
