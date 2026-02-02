/// <reference types="cypress" />

describe('nosher.net computer adverts - A-Z index', () => {
  

  it('Text version of advert works', () => {
    cy.request({
      method: 'GET',
      url: 'http://10.1.203.1:8010/archives/computers/pcw_1984-08-00_004_psion.txt',
      headers: {
        'Content-Type': 'text/plain',
      }
    }).then((response) => {
      expect(response.status).to.equal(200);
      expect(response.body).to.equal("\nOne way or another, you can have a computer in your pocket Launched in 1984, the Psion Organiser, billed by Psion as the \"world's first practical pocket computer\" is considered - at least by its second incarnation, the Organiser II - as the world's first usable PDA.  Within a year the machine had found a niche in specialist mo\n")
    })
  })
 

  it('Text version of indexed advert works', () => {
    cy.request({
      method: 'GET',
      url: 'http://10.1.203.1:8010/archives/computers/pcw_1984-08-00_004_psion.txt?idx=Charles',
      headers: {
        'Content-Type': 'text/plain',
      }
    }).then((response) => {
      expect(response.status).to.equal(200);
      expect(response.body).to.equal("\n...te a new, radical concept of a handheld computer.  The idea of a handheld computer was conceived by <span class=\"hilite\">Charles</span> Davies - a former student of Potter's when he was at Imperial College, London, and who was now Psion's Software Director - whilst the two were at lunch in a Greek restaurant.  As the company started work on its new project...\n")
    })
  })


  it('Text version of indexed advert contains highlight span and class', () => {
    cy.request({
      method: 'GET',
      url: 'http://10.1.203.1:8010/archives/computers/pcw_1984-08-00_004_psion.txt?idx=Charles',
      headers: {
        'Content-Type': 'text/plain',
      }
    }).then((response) => {
      expect(response.status).to.equal(200);
      expect(response.body).to.contain("span class=\"hilite\"")
    })
  })


  it('Text version of indexed advert does not contain highlight span and class for invalid index', () => {
    cy.request({
      method: 'GET',
      url: 'http://10.1.203.1:8010/archives/computers/pcw_1984-08-00_004_psion.txt?idx=XYXYXY',
      headers: {
        'Content-Type': 'text/plain',
      }
    }).then((response) => {
      expect(response.status).to.equal(200);
      expect(response.body).to.not.contain("span class=\"hilite\"")
    })
  })


  it('Text version of indexed advert contains match at end of long text', () => {
    cy.request({
      method: 'GET',
      url: 'http://10.1.203.1:8010/archives/computers/pcw_1984-08-00_004_psion.txt?idx=2012',
      headers: {
        'Content-Type': 'text/plain',
      }
    }).then((response) => {
      expect(response.status).to.equal(200);
      expect(response.body).to.contain("\n...nate the mobile phone market until the advent of the iPhone and Android in 2007.  Psion continued developing various netbooks and PDAs running EPOC up until 1999's series 7, but the market was moving to cheaper models like the Palm Pilot, and PDA's based upon Microsoft's Windows CE. Psion was eventually sold to Motorola in <span class=\"hilite\">2012</span>.\n")
    })
  })


  it('A-Z index has links for 0,1,2, etc, and A-Z', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/index')
    cy.get('div.catindex').find('p').eq(0).find('a').should('have.length', 30)
  })
  

  it('A-Z index has enough links in the A category', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/index')
    cy.get('ul.catalogue').find('li').should('have.length.above', 30)
  })


  it('A-Z index A category first link is correctly formed', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/index')
    cy.get('ul.catalogue').find('li').eq(0).find('a').first().then(($link) => {
      cy.wrap($link).find('span').first().should('have.text', "A&F Software")
      cy.wrap($link).should('have.attr', 'href')
        .and('include','/archives/computers/pcw_1982-12_36?idx=A%26F%20Software')
      cy.wrap($link).find('span').first()
      .should('have.attr', 'onmouseout')
      .and('include','popup_hide();')  
      cy.wrap($link).find('span').first()
      .should('have.attr', 'onmouseover')
      .and('include','popup_show(event, \'pcw_1982-12_36.txt?idx=A%26F%20Software\', this)')  
    })
  })


  it('A-Z index has enough links in the Z category', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/index/Z')
    cy.get('ul.catalogue').find('li').should('have.length.above', 30)
  })

  
  it('A-Z index has correct title in the Z category', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/index/Z')
    cy.get('div.catindex').find('p').eq(1).find('b').contains('Z')
  })


  it('A-Z index Z80H result should have multiple links', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/index/Z')
    cy.get('ul.catalogue').find('li').contains('Z80H').should('have.length', 1).then(($listitem) => {
      cy.wrap($listitem).find('a').should('have.length.above', 1)
      cy.wrap($listitem).find('a').eq(0).then(($link) => {
        cy.wrap($link).should('have.attr', 'href')
          .and('include','/archives/computers/microsoft_z80_percw_nov81?idx=Z80H')
        cy.wrap($link).should('have.attr', 'onmouseout')
          .and('include','popup_hide();')  
        cy.wrap($link).should('have.attr', 'onmouseover')
          .and('include','popup_show(event, \'microsoft_z80_percw_nov81.txt?idx=Z80H\', this)')
      })
    })
  })


})
