/// <reference types="cypress" />

describe('nosher.net photo album', () => {
  
  beforeEach(() => {
    // set viewport to over 1000 to avoid triggering mobile view
    cy.viewport(1100,660)
    cy.visit('http://10.1.203.1:8010/images/2025/2025-01-19WalkAroundDebenham/')
  })


  it('Check navmenu has links to photo years', () => {
    cy.get('p.navlink').should('have.length', 2).find('a').should(($link) => {
      expect($link.attr('href')).contains(/images/)
    })
  })


  it('Check page contains correct title', () => {
    cy.get('h1').should('have.length', 1).contains("A Pub Walk to the Lion")
  })


  it('Check there are a sensible number of photos', () => {
    cy.get('section.thumbnails').should('have.length', 1).should(($list) => {
      if ($list.find('article.thumb').length < 10 ) {
        throw new Error('Did not find photo thumbnails')
      }
    })
  })


  it('Click first photo to open viewer', () => {
    cy.get('article.thumb').first().click()
    cy.get('#viewer').should('be.visible')
    cy.get('img#fullsize').should('have.length', 1).should(($img) => {
      expect($img.attr('src')).contains("imgp0076")
    })
    cy.get('div#caption').contains("The moon rises")
  })
  

  it('Click first photo to open viewer then cursor right', () => {
    cy.get('article.thumb').first().click()
    cy.get('#viewer').should('be.visible')
    cy.get('img#fullsize').should('have.length', 1).should(($img) => {
      expect($img.attr('src')).contains("imgp0076")
    })
    cy.get('div#caption').contains("The moon rises")
    cy.get('photoview').trigger('keydown', {keyCode: 39, force: true});
    cy.get('img#fullsize').should('have.length', 1).should(($img) => {
      expect($img.attr('src')).contains("imgp0082")
    })
    cy.get('div#caption').contains("We spot Lucy the one-eyed cat")
  })


  it('Click first photo to open viewer then cursor left', () => {
    cy.get('article.thumb').first().click()
    cy.get('#viewer').should('be.visible')
    cy.get('img#fullsize').should('have.length', 1).should(($img) => {
      expect($img.attr('src')).contains("imgp0076")
    })
    cy.get('div#caption').contains("The moon rises")
    cy.get('photoview').trigger('keydown', {keyCode: 37, force: true});
    cy.get('#viewer').should('not.be.visible')
    cy.url().should('include', '2025-01-11DovePlayersPanto')
  })


  it('Click cursor left on photo album', () => {
    cy.get('photoview').trigger('keydown', {keyCode: 37, force: true});
    cy.get('#viewer').should('not.be.visible')
    cy.url().should('include', '2025-01-11DovePlayersPanto')
  })


  it('Click cursor right on photo album', () => {
    cy.get('photoview').trigger('keydown', {keyCode: 39, force: true});
    cy.get('#viewer').should('not.be.visible')
    cy.url().should('include', '2025-01-26PPWrapParty')
  })


  it('Click first photo to open viewer then cursor right, left', () => {
    cy.get('article.thumb').first().click()
    cy.get('#viewer').should('be.visible')
    cy.get('photoview').trigger('keydown', {keyCode: 39, force: true});
    cy.get('img#fullsize').should(($img) => {
      expect($img.attr('src')).contains("imgp0082")
    })
    cy.get('div#caption').contains("We spot Lucy the one-eyed cat")
    cy.get('photoview').trigger('keydown', {keyCode: 37, force: true});
    cy.get('img#fullsize').should(($img) => {
      expect($img.attr('src')).contains("imgp0076")
    })
    cy.get('div#caption').contains("The moon rises")
  })


  it('Check photo strip in viewer mode', () => {
    cy.get('article.thumb').first().click()
    cy.get('#viewer').should('be.visible')
    cy.get('section#strip').should(($strip) => {
      if ($strip.find('div').length < 10 ) {
        throw new Error('Did not find photo strip images')
      }
    })
  })


  it('Check photo opens in noJS mode', () => {
    cy.get('article.thumb').first().find('a').invoke('removeAttr', 'onclick').click()
    cy.url().should('include', 'nojs?year=2025&path=2025-01-19WalkAroundDebenham')
  })


  it('Click on photo in photo strip', () => {
    cy.get('article.thumb').first().find('a').click()
    cy.get('#viewer').should('be.visible')
    cy.get('section#strip').find('img').eq(4).click()
    cy.get('img#fullsize').should(($img) => {
      expect($img.attr('src')).contains("imgp0095")
    })
    cy.get('div#caption').contains("A tree has fallen over")
  })


  it('Load album with pre-set index, as if from a search result', () => {
    cy.visit('http://10.1.203.1:8010/images/2025/2025-01-19WalkAroundDebenham/4')
    cy.get('#viewer').should('be.visible')
    cy.get('img#fullsize').should(($img) => {
      expect($img.attr('src')).contains("imgp0095")
    })
    cy.get('div#caption').contains("A tree has fallen over")
  })

  
  it('X closes viewer', () => {
    cy.get('article.thumb').first().click()
    cy.get('#viewer').should('be.visible')
    cy.get('photoview').trigger('keydown', {keyCode: 88, force: true});
    cy.get('#viewer').should('not.be.visible')
  })

})
