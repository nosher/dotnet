/// <reference types="cypress" />

describe('nosher.net computer adverts - by filters', () => {


  it('Adverts by Models link is present', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/')
    cy.get('p.nav').find('a').eq(5).should('contain.text', 'by model')
  })
  

  it('Adverts by Models has 26 jump-to links ', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/models/')
    cy.get('section.archives').find('p').eq(1).find('a').should('have.length', 26)
  })
  

  it('Adverts by Models has 26 jump-to targets ', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/models/')
    cy.get('section.archives').find('a[name]').should('have.length', 26)
  })


  it('Adverts by Models check Acorn first advert goes straight to page', () => {
    // a single-advert model result should link straight to the target page
    cy.visit('http://10.1.203.1:8010/archives/computers/models/')
    cy.get('div.models').find('div').eq(0).find('a').contains('Archimedes').then(($link) => {
      const href = $link.prop('href')
      cy.visit(href)
      cy.url().should('contain', '/archives/computers/acorn_archie_percw_jan88')
    })
  })


  it('Adverts by Models check Acorn BBC Micro link goes to thumbnails page', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/models/')
    cy.get('div.models').find('div').eq(0).find('a').contains('BBC Micro (Proton)').then(($link) => {
      const href = $link.prop('href')
      cy.visit(href)
      cy.url().should('contain', '/archives/computers/model/BBC%20Micro%20(Proton)')
    })
  })


  it('Adverts by Models check model with / does not break', () => {
    // a single-advert model result should link straight to the target page
    cy.visit('http://10.1.203.1:8010/archives/computers/models/')
    cy.get('section.archives').find('div.models').eq(3).find('a').contains('DB 8/1').then(($link) => {
      const href = $link.prop('href')
      cy.visit(href)
      cy.url().should('contain', '/archives/computers/model/DB%208%7C1')
    })
  })

  
  it('Adverts by Models check Atari 520ST page has three links', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/model/520ST')
    cy.get('div#yearindex').find('div').should('have.length', 3)
  })


  it('Adverts by Models check Atari 520ST page first link', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/model/520ST')
    cy.get('div#yearindex').find('div').eq(0).find('a').then(($link) => {
      const href = $link.prop('href')
      cy.visit(href)
      cy.url().should('contain', '/archives/computers/your_computer_1985-12_001')
    })
  })
  

  it('Adverts by Models check Atari 520ST page first link thumbnail', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/model/520ST')
    cy.get('div#yearindex').find('div').eq(0).find('img').invoke('attr', 'src')
        .should('contain', '/archives/computers/images/your_computer_1985-12_001-s.webp')
  })


  it('By CPU link is present', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/?type=year&value=1980')
    cy.get('p.nav').find('a').eq(6).should('contain.text', 'by CPU')
  })


  it('Adverts by CPU', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/cpus/')
    cy.get('section.archives').find('h3').first().should('contain.text', '8-bit CPUs')
  })


  it('Adverts by CPU - first 8-bit link', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/cpus/')
    cy.get('section.archives').find('li').first().find('a').then(($link) => {
      const href = $link.prop('href')
      cy.visit(href)
      cy.url().should('contain', '/archives/computers/cpus/Capricorn')
      cy.get('main#cmain').find('h1').first().should('contain.text', "3 adverts that feature the Hewlett-Packard Capricorn")
    })
  })


  it('Adverts by CPU - single-advert 8-bit link', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/cpus/LH5801')
    cy.url().should('contain', '/archives/computers/sharp_pc1500_perscomp_may82')
  })


  it('Adverts by CPU - first 8-bit link text is correct', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/cpus/')
    cy.get('section.archives').find('li').first().find('p').first().should('contain.text', '16 bit address (64K memory max), proprietary HP CPU')
  })


  it('Adverts by CPU - check thumbnail image is present', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/cpus/Capricorn')
    cy.get('section.archives').find('a').first().find('img').should('have.length', 1).should('have.prop', 'src')
      .and('include', 'hp85_pcw_nov80-s.webp')
  })


  it('Adverts by CPU - check 70+ thumbnail images are present for 6502', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/cpus/6502')
    cy.get('section.archives').find('div#yearindex').find('img').should(($images) => {
      if ($images.length < 50 ) {
        throw new Error('Not enough thumbnails')
      }
    })
  })


  it('Adverts by CPU - visit the first 8-bit link', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/cpus/Capricorn')
    cy.get('section.archives').find('a').first().then(($link) => {
      const href = $link.prop('href')
      cy.visit(href)
      cy.url().should('contain', '/archives/computers/hp85_pcw_nov80')
    })
  })


  
})
