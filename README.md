# XML to UAT Evidence Generator

This script streamlines the User Acceptance Testing (UAT) evidence collection process for deployments managed via Control-M (or similar XML-based configuration).

It parses an XML file containing folder and job definitions and generates a structured Excel spreadsheet. Each sheet in the Excel file corresponds to a folder from the XML, listing the jobs within that folder. This provides a clear template for developers to add their testing evidence (e.g., screenshots) and for reviewers to easily locate and verify results for each deployment unit ('folder').

This approach replaces potentially confusing manual documentation processes involving multiple files and links.
