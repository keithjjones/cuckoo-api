#
# Imports
#
import requests
import json
import os


#
# The Main Function
#
def main():
    """
    Main function for this library
    """
    print("This is a library and not a script.  It cannot be run as a script.")
    pass


#
# Static Functions
#
def buildapiurl(proto="http", host="127.0.0.1", port=8000,
                action=None):
    """
    Create a URL for the Cuckoo API

    :param proto: http or https
    :param host: Hostname or IP address
    :param port: The port of the Cuckoo API server
    :param action: The action to perform with the API
    :returns: The URL

    """
    if action is None:
        return None
    else:
        return "{0}://{1}:{2}{3}".format(proto, host, port, action)


#
# Classes
#
class CuckooAPI(object):
    """
    Class to hold Cuckoo API data.
    """
    def __init__(self, host="127.0.0.1", port=8000, proto="http"):
        """

        :param host: Hostname or IP address of Cuckoo server
        :param port: The port of the Cuckoo server
        :param proto: http or https

        """
        self.proto = proto
        self.host = host
        self.port = port

    def getcuckoostatus(self):
        """
        Function to get the status of the Cuckoo instance.

        :returns: Returns the status as a dictionary.

        """
        # Build the URL
        apiurl = buildapiurl(self.proto, self.host, self.port,
                             "/cuckoo/status")

        request = requests.get(apiurl)

        jsonreply = json.loads(request.text)
        return jsonreply

    def listmachines(self):
        """
        Lists the machines available for analysis.

        :returns: Returns the list of machines as a list.

        """
        # Build the URL
        apiurl = buildapiurl(self.proto, self.host, self.port,
                             "/machines/list")
        request = requests.get(apiurl)

        jsonreply = json.loads(request.text)
        return jsonreply

    def viewmachine(self, vmname=None):
        """
        Lists the details about an analysis machine.

        :param vmname: The vm name for the machine to be listed
        :returns: Returns the dictionary of the machine specifics

        """
        # Build the URL
        if vmname is None:
            raise CuckooAPINoVM(vmname)

        apiurl = buildapiurl(self.proto, self.host, self.port,
                             "/machines/view/"+vmname)
        request = requests.get(apiurl)

        jsonreply = json.loads(request.text)
        return jsonreply

    def taskslist(self, limit=None, offset=None):
        """
        Lists the tasks in the Cuckoo DB.

        :param limit: Limit to this many results (Optional)
        :param offset: Offset the output to offset in the total task list
            and requires limit above. (Optional)
        :returns: Returns a list of task details.

        """
        # Build the URL
        baseurl = "/tasks/list"
        if limit is not None:
            baseurl = baseurl+"/"+str(limit)
            if offset is not None:
                baseurl = baseurl+"/"+str(offset)

        apiurl = buildapiurl(self.proto, self.host, self.port,
                             baseurl)
        request = requests.get(apiurl)

        jsonreply = json.loads(request.text)
        return jsonreply

    def taskview(self, taskid=None):
        """
        View the task for the task ID.

        :param taskid: The ID of the task to view.
        :returns: Returns a dict of task details.

        """
        # Build the URL
        if taskid is None or taskid < 1:
            raise CuckooAPINoTaskID(taskid)

        apiurl = buildapiurl(self.proto, self.host, self.port,
                             "/tasks/view/"+str(taskid))

        request = requests.get(apiurl)

        jsonreply = json.loads(request.text)
        return jsonreply

    def taskreport(self, taskid=None, reportformat="json"):
        """
        View the report for the task ID.

        :param taskid: The ID of the task to report.
        :param reportformat: Format of the data returned.
            Possible:  json/html/all/dropped/package_files
        :returns: Returns a dict report for the task if json format, raw
            data otherwise.

        """
        # Build the URL
        if taskid is None or taskid < 1:
            raise CuckooAPINoTaskID(taskid)

        apiurl = buildapiurl(self.proto, self.host, self.port,
                             "/tasks/report/"+str(taskid)+"/"+reportformat)

        # Error on any other format for now...
        if reportformat != "json":
            raise CuckooAPINotImplemented(apiurl)

        request = requests.get(apiurl)

        if reportformat == 'json':
            jsonreply = json.loads(request.text)
            return jsonreply
        else:
            return request.text

    def taskdelete(self, taskid=None):
        """
        Delete a task.

        :param taskid: The task ID to delete.
        :returns: Status

        """
        if taskid is None or taskid < 1:
            raise CuckooAPINoTaskID(taskid)

        apiurl = buildapiurl(self.proto, self.host, self.port,
                             "/tasks/delete/"+str(taskid))

        request = requests.get(apiurl)

        jsonreply = json.loads(request.text)
        return jsonreply

    def taskscreenshots(self, taskid=None, filepath=None, screenshot=None):
        """
        Download screenshot(s).

        :param taskid: The task ID for the screenshot(s).
        :param filepath: Where to save the screenshot(s).
            If you are using the Django web api the screenshots
            are saved as .tar.bz!
            If you are using the api.py script the screenshots are in .zip
            format.
            This function adds the apppropriate file extensions to the
            filepath variable.
        :param screenshot: The screenshot number to download.
        :returns: Nothing

        """
        if taskid is None or taskid < 1:
            raise CuckooAPINoTaskID(taskid)

        if filepath is None or os.path.exists(filepath):
            raise CuckooAPIFileExists(filepath)

        filepath = filepath+".zip"

        baseurl = "/tasks/screenshots/"+str(taskid)
        if screenshot is not None:
            baseurl = baseurl+"/"+str(screenshot)

        apiurl = buildapiurl(self.proto, self.host, self.port,
                             baseurl)

        # Turn on stream to download files
        request = requests.get(apiurl, stream=True)

        with open(filepath, 'wb') as f:
            # Read and write in chunks
            for chunk in request.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

    def submitfile(self, filepath, data=None):
        """
        Function to submit a local file to Cuckoo for analysis.

        :param filepath: Path to a file to submit.
        :param data: This is data containing any other options for the
            submission form.  This is a dict of values accepted by the
            create file options in the cuckoo API.  More form
            information can be found in the following link:
            https://downloads.cuckoosandbox.org/docs/usage/api.html#tasks-create-file
        :returns: Returns the json results of the submission

        """
        # Error if the file does not exist
        if (filepath is None or not os.path.exists(filepath) or
                not os.path.isfile(filepath)):
            raise CuckooAPIInvalidFileException(filepath)

        # Build the URL
        apiurl = buildapiurl(self.proto, self.host, self.port,
                             "/tasks/create/file")

        with open(filepath, "rb") as sample:
            # multipart_file = {"file": ("temp_file_name", sample)}
            multipart_file = {"file": (os.path.basename(filepath), sample)}
            request = requests.post(apiurl, files=multipart_file, data=data)

        jsonreply = json.loads(request.text)
        return jsonreply

    def submiturl(self, url, data=None):
        """
        Function to submit a URL to Cuckoo for analysis.

        :param url: URL to submit.
        :param data: This is data containing any other options for the
            submission form.  This is a dict of values accepted by the
            create file options in the cuckoo API.  More form
            information can be found in the following link:
            https://downloads.cuckoosandbox.org/docs/usage/api.html#tasks-create-url
        :returns: Returns the json results of the submission

        """
        # Build the URL
        apiurl = buildapiurl(self.proto, self.host, self.port,
                             "/tasks/create/url")

        multipart_url = {"url": ("", url)}
        request = requests.post(apiurl, files=multipart_url, data=data)

        jsonreply = json.loads(request.text)
        return jsonreply

    def fileview(self, hashid=None, hashtype=None):
        """
        View the details for the file given the hash.

        :param hashid: The hash or task ID to search.
        :param hashtype: The following types of hash:
            'id', 'md5', 'sha256'.  Any other values will cause
            an error!
        :returns: Returns the results of the file in a dict.

        """
        if hashid is None:
            raise CuckooAPINoHash(hashid, hashtype)

        # Get rid of ints
        hashid = str(hashid)

        # Build the URL
        apiurl = buildapiurl(self.proto, self.host, self.port,
                             "/files/view/"+hashtype+"/"+hashid)

        if hashtype != "md5" and hashtype != "id" and hashtype != "sha256":
            raise CuckooAPINotAvailable(apiurl)

        request = requests.get(apiurl)

        jsonreply = json.loads(request.text)
        return jsonreply

    def sampledownload(self, hashid=None,
                       filepath=None):
        """
        Download a file by hash.

        :param hashid: The SHA256 hash used to download the sample.
        :returns: Nothing

        """
        # Get rid of ints
        hashid = str(hashid)

        if filepath is None or os.path.exists(filepath):
            raise CuckooAPIFileExists(filepath)

        baseurl = "/files/get/"+hashid

        apiurl = buildapiurl(self.proto, self.host, self.port,
                             baseurl)

        # Turn on stream to download files
        request = requests.get(apiurl, stream=True)

        with open(filepath, 'wb') as f:
            # Read and write in chunks
            for chunk in request.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

    def pcapdownload(self, taskid=None, filepath=None):
        """
        Download a pcap by task ID.

        :param taskid: The task ID to download the pcap.
        :returns: Nothing

        """
        if taskid is None or taskid < 1:
            raise CuckooAPINoTaskID(taskid)

        if filepath is None or os.path.exists(filepath):
            raise CuckooAPIFileExists(filepath)

        baseurl = "/pcap/get/"+str(taskid)

        apiurl = buildapiurl(self.proto, self.host, self.port,
                             baseurl)

        # Turn on stream to download files
        request = requests.get(apiurl, stream=True)

        with open(filepath, 'wb') as f:
            # Read and write in chunks
            for chunk in request.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)


class CuckooAPIInvalidFileException(Exception):
    """
    Exception for when a file is not found.
    """
    def __init__(self, filepath):
        Exception.__init__(self, "CuckooAPI: Invalid File {0}".format(
                           filepath))


class CuckooAPINotImplemented(Exception):
    """
    Exception for when a call is not implemented, but is available.
    """
    def __init__(self, apicall):
        Exception.__init__(self,
                           "CuckooAPI: Not Implemented {}".format(apicall))


class CuckooAPINotAvailable(Exception):
    """
    Exception for when a call is not available on the remote server.
    This signifies you may have used an API call meant for the Django
    interface and sent it to the api.py interface, or vice versa.
    """
    def __init__(self, apicall):
        Exception.__init__(self, "CuckooAPI: This API is not available for "
                           "your target Cuckoo server.  Are you mixing "
                           "calls from Django web interface with the "
                           "api.py interface?  Or the other way around?")


class CuckooAPIBadRequest(Exception):
    """
    Exception for when a Cuckoo machine is not found.
    """
    def __init__(self, apiurl):
        Exception.__init__(self, "CuckooAPI:  Unable to connect "
                           "with URL {0}  Are you mixing "
                           "calls from Django web interface with the "
                           "api.py interface?  Or the other way "
                           "around?".format(apiurl))


class CuckooAPINoVM(Exception):
    """
    Exception for when a vm is not found.
    """
    def __init__(self, vmname):
        Exception.__init__(self, "CuckooAPI:  VM {0} not available or invalid!"
                           .format(vmname))


class CuckooAPINoTaskID(Exception):
    """
    Exception for when an invalid task ID is used.
    """
    def __init__(self, taskid):
        Exception.__init__(self, "CuckooAPI:  Task ID {0} not avilable or "
                           "invalid!".format(taskid))


class CuckooAPITaskNoDelete(Exception):
    """
    Exception for when a task cannot be deleted.
    """
    def __init__(self, taskid):
        Exception.__init__(self, "CuckooAPI: Task ID {0} cannot be "
                           "deleted!".format(taskid))


class CuckooAPINoHash(Exception):
    """
    Exception for when an invalid file hash is used.
    """
    def __init__(self, hashid, hashtype):
        Exception.__init__(self, "CuckooAPI:  Hash {0} of type {1} not "
                           "available or invalid!".format(hashid, hashtype))


class CuckooAPIFileExists(Exception):
    """
    Exception for when a file is about to be saved over an existing file
    or the file name is invalid.
    """
    def __init__(self, filepath):
        Exception.__init__(self, "CuckooAPI: {0} already exists or "
                           "is invalid!".format(filepath))

#
# Call main if run as a script
#
if __name__ == '__main__':
    main()
