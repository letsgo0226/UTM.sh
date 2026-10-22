import copy
import unittest
from control_plane import github_event, build
from railway_probe import collect, summarize, QUERY

ENV={"GITHUB_EVENT_NAME":"push","GITHUB_REPOSITORY":"letsgo0226/UTM.sh",
     "GITHUB_SHA":"a"*40,"GITHUB_REF":"refs/heads/everlife-open-sdg-v1","GITHUB_RUN_ID":"100"}

class EventBridgeTests(unittest.TestCase):
    def test_github_metadata_only(self):
        e=github_event(ENV,{"head_commit":{"message":"password=PRIVATE"}, "secret":"DO_NOT_PUBLISH"})
        self.assertEqual(e["status"],"OBSERVED_GITHUB_EVENT")
        self.assertNotIn("PRIVATE",str(e))
        self.assertNotIn("DO_NOT_PUBLISH",str(e))
        self.assertEqual(github_event(ENV,{}),e)

    def test_untrusted_event_rejected(self):
        x=copy.deepcopy(ENV)
        x["GITHUB_EVENT_NAME"]="repository_dispatch"
        self.assertEqual(github_event(x,{})["status"],"REJECTED_EVENT")
        x=copy.deepcopy(ENV)
        x["GITHUB_REPOSITORY"]="unknown/repo"
        self.assertEqual(github_event(x,{})["status"],"REJECTED_EVENT")

    def test_railway_offline(self):
        r=collect("","")
        self.assertEqual(r["status"],"NOT_CONFIGURED")
        self.assertNotIn("mutation", QUERY.lower())

    def test_summarize_only_counts(self):
        response={"data":{"project":{"name":"private-name","services":{"edges":[
           {"node":{"name":"hidden-service","serviceInstances":{"edges":[
               {"node":{"latestDeployment":{"status":"SUCCESS"}}}]}}},
           {"node":{"name":"hidden-service-2","serviceInstances":{"edges":[
               {"node":{"latestDeployment":{"status":"CRASHED"}}}]}}}]}}}}
        d=summarize(response)
        self.assertEqual(d["service_instance_counts_by_deployment_status"],{"SUCCESS":1,"CRASHED":1})
        self.assertNotIn("private-name",str(d))
        self.assertNotIn("hidden-service",str(d))
        with self.assertRaises(ValueError):
            summarize({"errors":[{"message":"denied"}],"data":None})

    def test_fallback_and_human_review(self):
        d=build(ENV,{},{"status":"NOT_CONFIGURED"})
        self.assertEqual(d["decision"],"OPERATOR_REVIEW_REQUIRED")
        self.assertEqual(d["virtual_scheduler"]["jobs"],6)
        self.assertFalse(d["external_apply"])
        self.assertEqual(d["deployments_triggered"],0)
        self.assertFalse(d["claims"]["infinite_physical_resources"])

    def test_invalid_event_denied(self):
        bad=copy.deepcopy(ENV)
        bad["GITHUB_SHA"]="bad"
        d=build(bad,{},{"status":"OBSERVED"})
        self.assertEqual(d["decision"],"REJECTED")

if __name__=="__main__":
    unittest.main()
