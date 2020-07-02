import base64

import gnupg
import requests
import json


def push_to_github(filename, acc, repo, branch, token, gpg_key_file, commiter_name, commiter_email, commit_message):
    # Content to push
    base64content = base64.b64encode(open(filename, "rb").read())

    base_url = "https://api.github.com/repos/" + acc + "/" + repo

    commit_url = base_url + "/commits/" + branch
    last_commit = requests.get(url=commit_url)

    last_commit = last_commit.json()
    last_commit_sha = last_commit["sha"]
    base_tree = last_commit['commit']['tree']['sha']

    blob_post_url = base_url + "/git/blobs"
    blob_content = json.dumps({"content": base64content.decode('utf-8'),
                               "encoding": "base64",
                               })
    blob_resp = requests.post(blob_post_url, data=blob_content, headers={"Content-Type": "application/json", "Authorization": "token " + token})

    blob_resp = blob_resp.json()
    blob_sha = blob_resp['sha']
    tree_url = base_url + "/git/trees"
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

    # commit object unique data

    commit_name = commiter_name
    commit_email = commiter_email
    # Date in Github format
    commit_date = "2020-07-02T13:13:00Z"
    # Same date in epooch format
    commit_date_epoch = "1593695580 +0000"
    # Note: You need a trailing space at the end but it's not included if you don't send it in the message.
    # Note 2: This could do with another test by moving this to the end of the commit_object_template;
    # be prepared for it to fail though.
    commit_message = commit_message + "\n"

    # Update commit template with values for this commit object
    # NOTE: Format for template is VERY sensitive. Every \n is important here.
    # TODO: This should be moved to a template helper file rather than encoded in the code here.
    commit_object_template="tree {tree_sha}\nparent {parent_sha}\nauthor {author_name} <{author_email}> {author_date}\ncommitter {commiter_name} <{commiter_email}> {commmiter_date}\n\n{message}"
    commit_object_template = commit_object_template.replace("{tree_sha}", new_tree_sha)
    commit_object_template = commit_object_template.replace("{parent_sha}", last_commit_sha)
    commit_object_template = commit_object_template.replace("{author_name}", commit_name)
    commit_object_template = commit_object_template.replace("{author_email}", commit_email)
    commit_object_template = commit_object_template.replace("{author_date}", commit_date_epoch)
    commit_object_template = commit_object_template.replace("{commiter_name}", commit_name)
    commit_object_template = commit_object_template.replace("{commiter_email}", commit_email)
    commit_object_template = commit_object_template.replace("{commmiter_date}", commit_date_epoch)
    commit_object_template = commit_object_template.replace("{message}", commit_message)

    # Sign the commit object
    sig = ""
    # Note: I found it helpful to put the results to intermediate files, so I could compare the results of:
    # gpg --verify -vv doc.sig commit.txt
    # git verify-commit -v --raw <commit_sha>
    # Leaving this here for your reference

    # commit_content = open("/Users/feosa/pgp/commit.txt", "w")
    # commit_content.write(commit_object_template)
    # commit_content.close()

    # Create PGP signature, using our existing key
    gpg = gnupg.GPG(gnupghome='/Users/feosa/pgp')
    with open(gpg_key_file, encoding='ascii') as f:
        key_data = f.read()
        # TODO: Don't need the return value here, just useful when debugging
        import_result = gpg.import_keys(key_data)
        # Make a detached armored ascii signature of the raw git commit that will be made
        sig = gpg.sign(commit_object_template, detach=True)
        # Leaving this here for your reference for intermediate files
        # sig_copy = open("/Users/feosa/pgp/doc.sig", "w")
        # sig_copy.write(str(sig))
        # sig_copy.close()

    # Commit via API
    commit_object = json.dumps({
        "message": commit_message,
        "author": {
            "name": commit_name,
            "email": commit_email,
            "date": commit_date
        },
        "committer": {
            "name": commit_name,
            "email": commit_email,
            "date": commit_date
        },
        "parents": [
            last_commit_sha
        ],
        "tree": new_tree_sha,
        "signature": str(sig)
    })

    post_commit_url = base_url + "/git/commits"
    commit_resp = requests.post(url=post_commit_url, data=commit_object, headers={"Content-Type": "application/json", "Authorization": "token " + token})

    commit_resp = commit_resp.json()

    # Update the head ref to the new commit in the chain
    commit_sha = commit_resp['sha']
    ref_url = base_url + "/git/refs/heads/master"
    ref_object = json.dumps({
        "sha": commit_sha,
        "force": True,
    })
    ref_resp = requests.patch(url=ref_url,data=ref_object,headers= {"Content-Type": "application/json", "Authorization": "token " + token})
    print(ref_resp)

# To get Gpg keys in export format: gpg --armor --export-secret-key <KEY_ID> > key.asc
push_to_github("<FILE_TO_UPLOAD>", '<GIT_USERNAME>', '<REPO>','<BRANCH>','<GIT_ACCESS_TOKEN>', '<PATH_TO_GPG_KEY', '<COMMIT_NAME>', '<COMMIT_EMAIL>')