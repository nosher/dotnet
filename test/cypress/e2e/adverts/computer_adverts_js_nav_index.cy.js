/// <reference types="cypress" />

describe('nosher.net computer adverts - home page', () => {
  
  beforeEach(() => {
    //cy.visit('http://10.1.203.1:8010/archives/computers/')
  })

  it('test AZ companies advert links match selected letter', () => {
    cy.viewport(1100,660)
    cy.visit('http://10.1.203.1:8010/archives/computers/?type=source&value=Camputers')
    cy.get('div#az').should('be.visible')
    cy.get('div.opener').find('a#az_B').should('not.have.class', 'az_selected')
    cy.get('div.opener').find('a#az_C').should('have.class', 'az_selected')
    cy.get('div#group_C')
      .should('have.class', 'sublist_shown')
      .find('a')
      .not("[href='/archives/computers/models/']")
      .not("[href='/archives/computers/cpus/']")
      .not("[href='/archives/computers/years/']")
      .each(($item) => {
        cy.wrap($item).invoke('text').should('match', /^C.*?/)
    })
  })

  it('test standard companies list appears without JavaSCript', () => {
    const url = 'http://10.1.203.1:8010/archives/computers'
    cy.intercept(url, (req) => {
      req.continue((res) => {
        //const regex = /<script>.*?<\/script>/gs
        const regex = new RegExp('<script id="azExpander">.*?</script>', "gs");
        var updated = res.body.replaceAll(regex, '')
        res.body = updated
        console.log(updated)

      })
    }).as('page')

    cy.viewport(1100,660)
    cy.visit(url)
    cy.get('p#companies').should('be.visible')
    cy.get('div#az').should('not.be.visible')
  })
  

  it('test AZ companies list appears with JavaSCript', () => {
    cy.viewport(1100,660)
    cy.visit('http://10.1.203.1:8010/archives/computers')
    cy.get('p#companies').should('not.be.visible')
    cy.get('div#az').should('be.visible')
  })


  it('test AZ companies list selects correct group', () => {
    cy.viewport(1100,660)
    cy.visit('http://10.1.203.1:8010/archives/computers')
    cy.get('p#companies').should('not.be.visible')
    cy.get('div#az').should('be.visible')
    cy.get('div.opener').find('a').eq(2).click()
    cy.get('div#group_C').should('be.visible')
    cy.get('div#group_D').should('not.be.visible')
  })

  it('test AZ companies selected group first link', () => {
    cy.viewport(1100,660)
    cy.visit('http://10.1.203.1:8010/archives/computers')
    cy.get('div.opener').find('a').eq(2).click()
    cy.get('div#group_C').find('a').first().click()
    cy.url().should('contain', '/archives/computers/?type=source&value=C/WP-Cortex')
  })

  it('test AZ companies correct letter is selected', () => {
    cy.viewport(1100,660)
    cy.visit('http://10.1.203.1:8010/archives/computers/?type=source&value=Camputers')
    cy.get('div#az').should('be.visible')
    cy.get('div.opener').find('a#az_B').should('not.have.class', 'az_selected')
    cy.get('div.opener').find('a#az_C').should('have.class', 'az_selected')
  })

})