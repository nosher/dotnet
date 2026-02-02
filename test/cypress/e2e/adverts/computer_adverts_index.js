/// <reference types="cypress" />


describe('nosher.net computer adverts - catalogue/index', () => {
 

  Cypress.Commands.add('checkAds', (flist) => {
    flist.each(($li) => {
      cy.request({url: "http://10.1.203.1:8010/archives/computers/" + $li.text(), failOnStatusCode: false}).then((resp) => {
          cy.log("Testing: ", $li.text())
          if (resp.status !== 200) {
            cy.log("Testing: ", $li.text(), " DOES NOT EXIST AS ACTUAL PAGE")
            //throw new Error("File " + $li.text() + " does not exist as actual page");
          }
        })
      }
    )
  })

  // split the tests up because Cypress hangs on to the connection so the
  // server runs out of sockets if all 500+ ads are done in one go

  it('Test all files are in database 0-100', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/index/list?offset=0')
    cy.checkAds(cy.get("li"))
  })

  it('Test all files are in database 100-199', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/index/list?offset=100')
    cy.checkAds(cy.get("li"))
  })

  it('Test all files are in database 200-299', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/index/list?offset=200')
    cy.checkAds(cy.get("li"))
  })

  it('Test all files are in database 300-399', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/index/list?offset=300')
    cy.checkAds(cy.get("li"))
  })

  it('Test all files are in database 400-499', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/index/list?offset=400')
    cy.checkAds(cy.get("li"))
  })

  it('Test all files are in database 500-599', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/index/list?offset=500')
    cy.checkAds(cy.get("li"))
  })
})
