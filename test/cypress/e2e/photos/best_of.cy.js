/// <reference types="cypress" />

describe('nosher.net best of photo albums', () => {
  
  beforeEach(() => {
    // set viewport to over 1000 to avoid triggering mobile view
    cy.viewport(1100,660)
    cy.visit('http://10.1.203.1:8010/images/best/graffiti')
  })


  it('Check index page contains correct title', () => {
    cy.visit('http://10.1.203.1:8010/images/best/')
    cy.get('#cmain').find("h1").contains("The best of nosher.net")
  })


  it('Check unknown best-of generates a 404', () => {
    cy.request({url: 'http://10.1.203.1:8010/images/best/ksajdhfg', failOnStatusCode: false})
      .its('status').should('equal', 404)
  })


  it('Check index page contains at least one link', () => {
    cy.visit('http://10.1.203.1:8010/images/best/')
    cy.get('ul.albums').then($list => {
      if ($list.find('li').length < 1 ) {
        throw new Error('Did not find best-of photo albums')
      }
    })
  })


  it('Check photo opens in noJS mode', () => {
    cy.get('article.thumb').first().find('a').invoke('removeAttr', 'onclick').click()
    cy.url().should('include', 'nojs?year=2024&path=2024-05-29SuttonHooShip&thumb=34')
    cy.get('div.advert').find('img').should(($img) => {
      const alt = "Graffiti at the skate park, from The Sutton Hoo Ship Reconstruction, The Longshed, Woodbridge - 29th May 2024"
      expect($img.attr('alt')).contains(alt)
      expect($img.attr('title')).contains(alt)
    })
  })


  it('Check navmenu has links to photo years', () => {
    cy.get('p.navlink').should('have.length', 2).find('a').should(($link) => {
      expect($link.attr('href')).contains(/images/)
    })
  })


  it('Check page contains correct title', () => {
    cy.get('h1').should('have.length', 1).contains("Best of: Graffiti and Urban Decay")
  })


  it('Check there are a sensible number of photos', () => {
    cy.get('section.thumbnails').should('have.length', 1).should(($list) => {
      if ($list.find('article.thumb').length < 5 ) {
        throw new Error('Did not find photo thumbnails')
      }
    })
  })


  it('Check image caption has best-of subtitle', () => {
    cy.get('section.thumbnails').should('have.length', 1)
      .find("article.thumb").first()
      .find("p.subcaption")
      .contains('From: The Sutton Hoo Ship Reconstruction, The Longshed, Woodbridge - 29th May 2024')
  })


  it('Click first photo to open viewer', () => {
    cy.get('article.thumb').first().click()
    cy.get('#viewer').should('be.visible')
    cy.get('img#fullsize').should('have.length', 1).should(($img) => {
      expect($img.attr('src')).contains("imgp2533")
    })
    cy.get('div#caption').contains("Graffiti at the skate park")
  })
  

  it('Click first photo to open viewer then cursor right', () => {
    cy.get('article.thumb').first().click()
    cy.get('#viewer').should('be.visible')
    cy.get('img#fullsize').should('have.length', 1).should(($img) => {
      expect($img.attr('src')).contains("imgp2533")
    })
    cy.get('div#caption').contains("Graffiti at the skate park")
    cy.get('photoview').trigger('keydown', {keyCode: 39, force: true});
    cy.get('img#fullsize').should('have.length', 1).should(($img) => {
      expect($img.attr('src')).contains("imgp1640")
    })
    cy.get('div#caption').contains("Bright graffiti by the old Blackrock lido")
  })


  it('Click first photo to open viewer then cursor left', () => {
    cy.get('article.thumb').first().click()
    cy.get('#viewer').should('be.visible')
    cy.get('img#fullsize').should('have.length', 1).should(($img) => {
      expect($img.attr('src')).contains("imgp2533")
    })
    cy.get('div#caption').contains("Graffiti at the skate park")
    cy.get('photoview').trigger('keydown', {keyCode: 37, force: true});
    // left cursors don't do anything in "best of"
    cy.get('#viewer').should('be.visible')
    cy.url().should('include', '/best/graffiti')
  })


  it('Click first photo to open viewer then click "goto" link', () => {
    cy.get('article.thumb').first().click()
    cy.get('#viewer').should('be.visible')
    cy.get('div#subcaption').parent().click()
    cy.url().should('include', '/2024/2024-05-29SuttonHooShip')
  })


  it('Click cursor left on photo album does nothing', () => {
    cy.get('photoview').trigger('keydown', {keyCode: 37, force: true});
    cy.get('#viewer').should('not.be.visible')
    cy.url().should('include', '/best/graffiti')
  })


  it('Click cursor right on photo album does nothing', () => {
    cy.get('photoview').trigger('keydown', {keyCode: 39, force: true});
    cy.get('#viewer').should('not.be.visible')
    cy.url().should('include', '/best/graffiti')
  })


  it('Click first photo to open viewer then cursor right, left', () => {
    cy.get('article.thumb').first().click()
    cy.get('#viewer').should('be.visible')
    cy.get('photoview').trigger('keydown', {keyCode: 39, force: true});
    cy.get('img#fullsize').should(($img) => {
      expect($img.attr('src')).contains("imgp1640")
    })
    cy.get('div#caption').contains("Bright graffiti by the old Blackrock lido")
    cy.get('photoview').trigger('keydown', {keyCode: 37, force: true});
    cy.get('img#fullsize').should(($img) => {
      expect($img.attr('src')).contains("imgp2533")
    })
    cy.get('div#caption').contains("Graffiti at the skate park")
  })


  it('Check photo strip in viewer mode', () => {
    cy.get('article.thumb').first().click()
    cy.get('#viewer').should('be.visible')
    cy.get('section#strip').should(($strip) => {
      if ($strip.find('div').length < 5 ) {
        throw new Error('Did not find photo strip images')
      }
    })
  })


  it('Click on photo in photo strip', () => {
    cy.get('article.thumb').first().find('a').click()
    cy.get('#viewer').should('be.visible')
    cy.get('section#strip').find('img').eq(4).click()
    cy.get('img#fullsize').should(($img) => {
      expect($img.attr('src')).contains("TheDeadZoo/imgp1282")
    })
    cy.get('div#caption').contains("We cross over the rails on a graffiti bridge")
  })

  
  it('X closes viewer', () => {
    cy.get('article.thumb').first().click()
    cy.get('#viewer').should('be.visible')
    cy.get('photoview').trigger('keydown', {keyCode: 88, force: true});
    cy.get('#viewer').should('not.be.visible')
  })

})