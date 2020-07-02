import base64

import requests
import json

def push_to_github(filename, repo, branch, token):
    commit_url = "https://api.github.com/repos/foesa/" +repo+"/commits/"+branch
    last_commit = requests.get(url=commit_url)
    last_commit = last_commit.json()
    last_commit_sha = last_commit["sha"]
    base_tree = last_commit['commit']['tree']['sha']
    file_sha = last_commit['files'][0]['sha']
    base64content = base64.b64encode(open(filename,"rb").read())
    blob_post_url = "https://api.github.com/repos/foesa/"+repo+"/git/blobs"
    blob_content = json.dumps({"content": base64content.decode('utf-8'),
                               "encoding": "base64",
                               })
    blob_resp = requests.post(blob_post_url, data=blob_content, headers={"Content-Type": "application/json", "Authorization": "token " + token})
    blob_resp = blob_resp.json()
    blob_sha = blob_resp['sha']
    tree_url = "https://api.github.com/repos/foesa/"+repo+"/git/trees"
    tree_object = json.dumps({
        "base_tree": base_tree,
        "tree": [
            {
                "path": "Gittester/testdirectory/testfile.txt",
                "mode": "100644",
                "type": "blob",
                "sha": blob_sha
            }
        ]
    })
    tree_resp = requests.post(url=tree_url, data=tree_object, headers={"Content-Type": "application/json", "Authorization": "token " + token})
    new_tree_sha = tree_resp.json()
    new_tree_sha = new_tree_sha["sha"]
    commit_object = json.dumps({
        "message": "testing whole system",
        "parents": [
            last_commit_sha
        ],
        "tree": new_tree_sha,
        "signature": "-----BEGIN PGP SIGNATURE-----\n\n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\nrQ+klNJ3AO8o5J0FdGgXTcFt9RfJFg==\n=FeOm\n-----END PGP SIGNATURE-----\n"
    })
    post_commit_url = "https://api.github.com/repos/foesa/"+repo+"/git/commits"
    commit_resp = requests.post(url=post_commit_url, data=commit_object, headers={"Content-Type": "application/json", "Authorization": "token " + token})
    commit_resp = commit_resp.json()
    commit_sha = commit_resp['sha']
    ref_url = "https://api.github.com/repos/foesa/" +repo+"/git/refs/heads/master"
    ref_object = json.dumps({
        "sha": commit_sha,
        "force": True,
    })
    ref_resp = requests.patch(url=ref_url,data=ref_object,headers= {"Content-Type": "application/json", "Authorization": "token " + token})
    print(ref_resp)
    '''
    #data = requests.get(url+'?ref='+branch, headers = {"Authorization": "token "+token}).json()
    #data = requests.get(url+"/Gittester/testdirectory/testfile.txt" +'?ref='+branch, headers = {"Authorization": "token "+token}).json()
    try:
        url = url+"/Gittester/testdirectory/testfile.txt"
        sha = data['sha']
        if base64content.decode('utf-8') + "\n" != data['content']:
            message = json.dumps({"message": "update",
                                  "branch": branch,
                                  "content": base64content.decode("utf-8"),
                                  "sha": sha,
                                  "signature": '-----BEGIN PGP PUBLIC KEY BLOCK-----\n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\nrQ+klNJ3AO8o5J0FdGgXTcFt9RfJFg==\n=FeOm\n-----END PGP PUBLIC KEY BLOCK-----\n'
                                  })
            resp = requests.put(url, data=message,
                                headers={"Content-Type": "application/json", "Authorization": "token " + token})
            print(json.dumps(json.loads(resp.content),indent=4,sort_keys=True))
        else:
            print("nothing to update")
    except KeyError:
        print('SHa non existent')
        url = url + '/Gittester/testdirectory/testfile.txt'
        message = json.dumps({"message": "update",
                              "branch": branch,
                              "content": base64content.decode("utf-8"),
                              })

        resp = requests.put(url, data=message,
                            headers={"Content-Type": "application/json", "Authorization": "token " + token})
        print(resp)
        '''

push_to_github("/Users/foesa/PycharmProjects/Gittester/testdirectory/testfile.txt",'gtest','master',
               '5d4085a42b4e632833776af5ec9e1923d8c81c21')