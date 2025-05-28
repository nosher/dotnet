/// <reference types="cypress" />

describe('nosher.net photo album mobile', () => {
  
  beforeEach(() => {
    // set viewport to 320,480 to trigger mobile view
    cy.viewport('samsung-s10', 'portrait')
    cy.visit('http://10.1.203.1:8010/images/2025/2025-01-19WalkAroundDebenham/')
  })
  
  
  it('Check desktop viewer and photo strip are hidden in viewer mode', () => {
    cy.get('article.thumb').first().click()
    cy.get('#viewer').should('not.be.visible')
    cy.get('section#strip').should('not.be.visible')
  })


  it('Click first photo to open viewer', () => {
    cy.get('article.thumb').first().click()
    cy.get('#mobile_viewer').should('be.visible')
  })


  it('Check fourth photo is in view after open viewer from fourth thumbnail', () => {
    cy.get('article.thumb').eq(4).find('a').click()
    cy.get('#mobile_viewer').should('be.visible')
    cy.get("div#mphoto_4").then( $el => {
      const bottom = Cypress.$( cy.state("window") ).height();
      const rect = $el[0].getBoundingClientRect();
      expect( rect.top ).to.be.eq(0);
      expect( rect.bottom ).to.be.lessThan(bottom);
    });
  })


  it('Click first photo to open viewer and check height has been set', () => {
    cy.get('article.thumb').first().click()
    cy.get('#mobile_viewer').should('be.visible')
    cy.get('img#imgp0076').invoke('height').should('gt', 0)
    cy.get('img#imgp0076').invoke('width').should('gt', 0)
    // this album has a dimensions file, so images should be set to sizes
    // which reflect their aspect ratio and the window width
    cy.get('img#imgp0076').invoke('attr', 'data-dimensions').should('eq', 'true')
  })


  it('Click first photo to open viewer and check height has been set from natural dimensions', () => {
    // this album has no dimensions, so images should be set to their natural dimensions
    cy.visit('http://10.1.203.1:8010/images/2003/2003-12-18ATripToPlymouth/')
    cy.get('article.thumb').first().click()
    cy.get('#mobile_viewer').should('be.visible')
    cy.get('img#dcp_7477').invoke('height').should('gt', 0)
    cy.get('img#dcp_7477').invoke('width').should('gt', 0)
    cy.get('img#dcp_7477').invoke('attr', 'data-dimensions').should('eq', 'false')
  })


  it('Click first photo to open viewer and check height has been set from dimensions', () => {
    // check a "best of" album, which has virtual images from other albums, that CSS height has been
    // set via the graffiti_dimensions.txt file
    cy.visit('http://10.1.203.1:8010/images/best/graffiti')
    cy.get('article.thumb').first().click()
    cy.get('#mobile_viewer').should('be.visible')
    cy.get('img#2024-05-29SuttonHooShip_imgp2533').invoke('height').should('gt', 0)
    cy.get('img#2024-05-29SuttonHooShip_imgp2533').invoke('width').should('gt', 0)
    cy.get('img#2024-05-29SuttonHooShip_imgp2533').invoke('attr', 'data-dimensions').should('eq', 'true')
  })

})
