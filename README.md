# voila.naturalcapitalproject.org

This project contains jupyter notebooks and a `voila`-based application to serve a small web
application that allowed visitors to clip out an area of a large global dataset using a
user-defined bounding box.

The application was served on a VM, behind an nginx reverse proxy that also served a
LetsEncrypt-managed HTTPS certificate.

We shut down this service on 2025-04-29 because the clipping functionality is superceded
by the functionality of our Data Hub, https://data.naturalcapitalproject.stanford.edu.
